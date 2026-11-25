import re
from datetime import datetime, timedelta
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_local_now
from app.core.database import get_db
from app.api.deps import verify_bot_or_public_access, require_not_read_only
from app.models.attendance import AttendanceLog, AttendanceEventType, AttendanceStatus
from app.models.parent import Parent, student_parents
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from app.schemas.parent_order import ParentLinkRequest, ParentLinkStudentRequest
from app.services.audit_service import record_audit, get_role_str

router = APIRouter()


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 9:
        digits = "998" + digits
    elif digits.startswith("8") and len(digits) == 10:
        digits = "998" + digits[1:]
    return f"+{digits}" if digits else raw.strip()


@router.post("/link", summary="Ota-onani Telegram bot orqali bog'lash")
async def link_parent_telegram(
    payload: ParentLinkRequest,
    _: None = Depends(verify_bot_or_public_access),
    db: AsyncSession = Depends(get_db),
) -> Any:
    norm_phone = normalize_phone(payload.phone_number)
    raw_phone = payload.phone_number.strip()

    # Avval telefon raqami bo'yicha, so'ng chat_id bo'yicha qidirish
    res = await db.execute(
        select(Parent)
        .options(selectinload(Parent.students))
        .filter((Parent.phone_number == norm_phone) | (Parent.phone_number == raw_phone))
    )
    parent = res.scalar_one_or_none()

    if not parent:
        res_chat = await db.execute(
            select(Parent)
            .options(selectinload(Parent.students))
            .filter(Parent.telegram_chat_id == payload.telegram_chat_id)
        )
        parent = res_chat.scalar_one_or_none()

    if parent:
        parent.telegram_chat_id = payload.telegram_chat_id
        parent.phone_number = norm_phone
        parent.is_verified = True
        if payload.full_name and not parent.full_name:
            parent.full_name = payload.full_name.strip()
    else:
        parent = Parent(
            full_name=(payload.full_name or "Ota-ona").strip(),
            phone_number=norm_phone,
            telegram_chat_id=payload.telegram_chat_id,
            is_verified=True,
        )
        db.add(parent)

    await db.commit()
    await db.refresh(parent)

    res_children = await db.execute(
        select(Student)
        .join(student_parents, Student.id == student_parents.c.student_id)
        .filter(student_parents.c.parent_id == parent.id)
    )
    children = res_children.scalars().all()

    return {
        "success": True,
        "parent_id": parent.id,
        "phone_number": parent.phone_number,
        "children_count": len(children),
        "message": "Telefon raqamingiz EDUGATE tizimiga muvaffaqiyatli bog'landi.",
    }


@router.get("/{chat_id}/children", summary="Ota-onaga biriktirilgan farzandlar va bugungi holati")
async def get_parent_children(
    chat_id: int,
    _: None = Depends(verify_bot_or_public_access),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    parent = (
        await db.execute(
            select(Parent)
            .options(selectinload(Parent.students).selectinload(Student.school))
            .filter(Parent.telegram_chat_id == chat_id)
        )
    ).scalar_one_or_none()
    if not parent or not parent.students:
        return []

    today_start = datetime.combine(get_local_now().date(), datetime.min.time())
    output = []
    for st in parent.students:
        logs = (
            await db.execute(
                select(AttendanceLog)
                .options(selectinload(AttendanceLog.device))
                .filter(AttendanceLog.student_id == st.id, AttendanceLog.event_time >= today_start)
                .order_by(AttendanceLog.event_time.asc())
            )
        ).scalars().all()

        first_entry = next((l for l in logs if l.event_type == AttendanceEventType.ENTRY), None)
        last_exit = next((l for l in reversed(logs) if l.event_type == AttendanceEventType.EXIT), None)

        if first_entry and last_exit and last_exit.event_time > first_entry.event_time:
            today_status = f"Maktabdan chiqdi ({last_exit.event_time.strftime('%H:%M')})"
        elif first_entry:
            today_status = (
                "Kechikib keldi" if first_entry.status == AttendanceStatus.LATE else "Maktabda (O'z vaqtida)"
            )
        else:
            today_status = "Hali kelmagan"

        output.append({
            "id": st.id,
            "first_name": st.first_name,
            "last_name": st.last_name,
            "full_name": st.full_name,
            "student_code": st.student_code,
            "pinfl": st.pinfl,
            "class_name": st.class_name,
            "school_id": st.school_id,
            "school_name": st.school.name if st.school else "Biriktirilmagan",
            "has_face_id": bool(st.face_encoding or st.photo_path),
            "today_status": today_status,
            "entry_time": first_entry.event_time.strftime("%H:%M:%S") if first_entry else None,
            "exit_time": last_exit.event_time.strftime("%H:%M:%S") if last_exit else None,
            "device_name": first_entry.device.name if (first_entry and first_entry.device) else None,
        })
    return output


@router.get("/{chat_id}/monthly-report", summary="Ota-ona uchun joriy oy davomat hisoboti")
async def get_parent_monthly_report(
    chat_id: int,
    _: None = Depends(verify_bot_or_public_access),
    db: AsyncSession = Depends(get_db),
) -> Any:
    parent = (
        await db.execute(
            select(Parent)
            .options(selectinload(Parent.students))
            .filter(Parent.telegram_chat_id == chat_id)
        )
    ).scalar_one_or_none()
    if not parent or not parent.students:
        return {"linked": False, "children": []}

    now = get_local_now()
    month_start = datetime(now.year, now.month, 1)

    # Count weekdays elapsed in current month up to today
    study_days = 0
    cursor = month_start.date()
    while cursor <= now.date():
        if cursor.weekday() < 6:  # Mon-Sat school week in Uzbekistan
            study_days += 1
        cursor += timedelta(days=1)

    children_reports = []
    for st in parent.students:
        logs = (
            await db.execute(
                select(AttendanceLog)
                .filter(
                    AttendanceLog.student_id == st.id,
                    AttendanceLog.event_time >= month_start,
                    AttendanceLog.event_type == AttendanceEventType.ENTRY,
                )
                .order_by(AttendanceLog.event_time.asc())
            )
        ).scalars().all()

        # Deduplicate per day using earliest entry
        day_status = {}
        for l in logs:
            d_key = l.event_time.date()
            if d_key not in day_status:
                day_status[d_key] = l.status

        present_days = len(day_status)
        on_time_days = sum(1 for st_val in day_status.values() if st_val == AttendanceStatus.ON_TIME)
        late_days = sum(1 for st_val in day_status.values() if st_val == AttendanceStatus.LATE)
        rate = round((present_days / study_days) * 100, 1) if study_days > 0 else 0.0

        children_reports.append({
            "student_id": st.id,
            "student_name": st.full_name,
            "class_name": st.class_name,
            "study_days": study_days,
            "present_days": present_days,
            "on_time_days": on_time_days,
            "late_days": late_days,
            "missed_days": max(0, study_days - present_days),
            "attendance_rate": min(100.0, rate),
        })

    return {
        "linked": True,
        "month_label": now.strftime("%Y-%m"),
        "children": children_reports,
    }


@router.get("/{chat_id}/school-info", summary="Ota-onaning farzandi o'qiydigan maktab ma'lumotlari")
async def get_parent_school_info(
    chat_id: int,
    _: None = Depends(verify_bot_or_public_access),
    db: AsyncSession = Depends(get_db),
) -> Any:
    parent = (
        await db.execute(
            select(Parent)
            .options(selectinload(Parent.students).selectinload(Student.school))
            .filter(Parent.telegram_chat_id == chat_id)
        )
    ).scalar_one_or_none()
    if not parent or not parent.students:
        return {"linked": False, "schools": []}

    seen_schools = set()
    schools_info = []
    for st in parent.students:
        if not st.school or st.school_id in seen_schools:
            continue
        seen_schools.add(st.school_id)
        teacher = (
            await db.execute(
                select(Teacher).filter(
                    Teacher.school_id == st.school_id,
                    Teacher.class_name == st.class_name,
                    Teacher.is_active == True,
                )
            )
        ).scalar_one_or_none()
        schools_info.append({
            "school_name": st.school.name,
            "school_code": st.school.code,
            "address": st.school.address,
            "phone": st.school.phone,
            "class_name": st.class_name,
            "class_teacher": teacher.full_name if teacher else None,
            "class_teacher_phone": teacher.phone_number if teacher else None,
        })

    return {"linked": True, "schools": schools_info}


@router.post("/link-student", status_code=status.HTTP_201_CREATED, summary="Admin panel orqali ota-onani o'quvchiga biriktirish")
async def admin_link_parent_student(
    request: Request,
    payload: ParentLinkStudentRequest,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    student = (
        await db.execute(select(Student).options(selectinload(Student.parents)).filter(Student.id == payload.student_id))
    ).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    if (
        get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value
        and student.school_id != current_user.school_id
    ):
        raise HTTPException(status_code=403, detail="Boshqa maktab o'quvchisiga ota-ona biriktirish taqiqlangan.")

    norm_phone = normalize_phone(payload.phone_number)
    parent = (
        await db.execute(select(Parent).filter(Parent.phone_number == norm_phone))
    ).scalar_one_or_none()
    if not parent:
        parent = Parent(
            full_name=payload.full_name.strip(),
            phone_number=norm_phone,
            is_verified=False,
        )
        db.add(parent)
        await db.flush()
    elif payload.full_name.strip():
        parent.full_name = payload.full_name.strip()

    if all(p.id != parent.id for p in student.parents):
        student.parents.append(parent)

    await record_audit(
        db,
        user=current_user,
        action="PARENT_LINK_STUDENT",
        target_type="STUDENT",
        target_id=student.id,
        details=f"Ota-ona {parent.full_name} ({parent.phone_number}) -> {student.full_name}",
        request=request,
    )
    await db.commit()

    return {
        "message": "Ota-ona o'quvchiga muvaffaqiyatli biriktirildi!",
        "parent_id": parent.id,
        "phone_number": parent.phone_number,
        "student_id": student.id,
    }
