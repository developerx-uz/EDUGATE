from typing import List, Optional, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_local_now
from app.core.database import get_db
from app.api.deps import (
    get_current_device,
    get_current_user,
    require_not_read_only,
    verify_bot_or_public_access,
)
from app.models.absence import AbsenceRequest
from app.models.attendance import AttendanceLog, AttendanceEventType
from app.models.device import Device
from app.models.parent import Parent
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.attendance import (
    AttendanceEventCreate,
    AttendanceEventResponse,
    AttendanceLogOut,
    AbsenceReasonCreate,
    AbsenceReasonOut,
    AbsenceStatusUpdate,
)
from app.services.attendance_service import AttendanceService
from app.services.audit_service import record_audit, get_role_str
from app.services.notifier import notifier

router = APIRouter()


def _serialize_log(log: AttendanceLog) -> AttendanceLogOut:
    student = log.student
    school = student.school if student else None
    device = log.device
    return AttendanceLogOut(
        id=log.id,
        student_id=log.student_id,
        student_name=student.full_name if student else "Noma'lum",
        student_code=student.student_code if student else None,
        school_id=student.school_id if student else None,
        school_name=school.name if school else None,
        device_name=device.name if device else "Turniket",
        class_name=student.class_name if student else "",
        event_type=log.event_type,
        status=log.status,
        event_time=log.event_time,
        confidence=log.confidence,
        snapshot_path=log.snapshot_path,
        is_notified=log.is_notified,
    )


@router.post("/event", response_model=AttendanceEventResponse, summary="Kamera yoki Turniketdan davomat hodisasini qabul qilish")
async def receive_attendance_event(
    event: AttendanceEventCreate,
    background_tasks: BackgroundTasks,
    device: Device = Depends(get_current_device),
    db: AsyncSession = Depends(get_db),
):
    return await AttendanceService.process_event(
        db=db,
        event=event,
        device=device,
        background_tasks=background_tasks,
    )


@router.get("/today", response_model=List[AttendanceLogOut], summary="Kunlik davomat loglari (Sana va filtrlar bilan)")
async def get_today_attendance(
    school_id: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    date_str: Optional[str] = Query(None, alias="date"),
    limit: int = Query(200, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role_str = get_role_str(current_user)
    if role_str == UserRole.SCHOOL_ADMIN.value and current_user.school_id:
        school_id = current_user.school_id

    target_date = get_local_now().date()
    if date_str:
        try:
            target_date = date.fromisoformat(date_str.strip())
        except ValueError:
            raise HTTPException(status_code=400, detail="Sana formati YYYY-MM-DD bo'lishi kerak.")

    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date, datetime.max.time())

    query = (
        select(AttendanceLog)
        .join(AttendanceLog.student)
        .options(
            selectinload(AttendanceLog.student).selectinload(Student.school),
            selectinload(AttendanceLog.device),
        )
        .filter(AttendanceLog.event_time >= day_start, AttendanceLog.event_time <= day_end)
    )

    if school_id:
        query = query.filter(Student.school_id == school_id)
    if class_name:
        query = query.filter(Student.class_name.ilike(f"%{class_name.strip()}%"))
    if status_filter:
        query = query.filter(AttendanceLog.status == status_filter.strip().upper())

    query = query.order_by(AttendanceLog.event_time.desc()).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    return [_serialize_log(log) for log in logs]


@router.get("/student/{student_id}/today", summary="O'quvchining bugungi davomat holati (Bot va Kabinet uchun)")
async def get_student_today_attendance(
    student_id: str,
    _: None = Depends(verify_bot_or_public_access),
    db: AsyncSession = Depends(get_db),
) -> Any:
    student = (
        await db.execute(
            select(Student).options(selectinload(Student.school)).filter(Student.id == student_id)
        )
    ).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    today = get_local_now().date()
    day_start = datetime.combine(today, datetime.min.time())
    logs_res = await db.execute(
        select(AttendanceLog)
        .options(selectinload(AttendanceLog.device))
        .filter(AttendanceLog.student_id == student_id, AttendanceLog.event_time >= day_start)
        .order_by(AttendanceLog.event_time.asc())
    )
    logs = logs_res.scalars().all()

    first_entry = next((l for l in logs if l.event_type == AttendanceEventType.ENTRY), None)
    last_exit = next((l for l in reversed(logs) if l.event_type == AttendanceEventType.EXIT), None)

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "class_name": student.class_name,
        "school_name": student.school.name if student.school else None,
        "present_today": first_entry is not None,
        "entry_time": first_entry.event_time.strftime("%H:%M:%S") if first_entry else None,
        "entry_status": first_entry.status.value if first_entry else "ABSENT",
        "entry_device": first_entry.device.name if (first_entry and first_entry.device) else None,
        "exit_time": last_exit.event_time.strftime("%H:%M:%S") if last_exit else None,
        "events_count": len(logs),
    }


@router.post("/absence-reason", status_code=status.HTTP_201_CREATED, summary="Sababli dars qoldirish arizasini yuborish")
async def submit_absence_reason(
    payload: AbsenceReasonCreate,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_bot_or_public_access),
    db: AsyncSession = Depends(get_db),
) -> Any:
    student = (
        await db.execute(
            select(Student).options(selectinload(Student.school)).filter(Student.id == payload.student_id)
        )
    ).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    parent_id = None
    if payload.parent_chat_id:
        parent = (
            await db.execute(select(Parent).filter(Parent.telegram_chat_id == payload.parent_chat_id))
        ).scalar_one_or_none()
        if parent:
            parent_id = parent.id

    absence_date = payload.date or get_local_now().date().isoformat()
    req = AbsenceRequest(
        student_id=student.id,
        parent_id=parent_id,
        reason=payload.reason.strip(),
        absence_date=absence_date,
        document_url=payload.document_url,
        status="PENDING",
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)

    background_tasks.add_task(
        notifier.send_admin_alert,
        text=(
            f"📝 <b>Yangi Sababli Ariza</b>\n\n"
            f"👤 <b>O'quvchi:</b> {student.full_name} ({student.class_name})\n"
            f"🏫 <b>Maktab:</b> {student.school.name if student.school else '-'}\n"
            f"📅 <b>Sana:</b> {absence_date}\n"
            f"💬 <b>Sabab:</b> {req.reason}"
        ),
    )

    return {
        "id": req.id,
        "status": req.status,
        "student_name": student.full_name,
        "absence_date": req.absence_date,
        "message": "Sababli dars qoldirish arizasi qabul qilindi.",
    }


@router.get("/absence-reasons", response_model=List[AbsenceReasonOut], summary="Sababli dars qoldirish arizalari ro'yxati")
async def list_absence_reasons(
    school_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    role_str = get_role_str(current_user)
    effective_school_id = (
        current_user.school_id if role_str == UserRole.SCHOOL_ADMIN.value else school_id
    )

    query = (
        select(AbsenceRequest)
        .join(AbsenceRequest.student)
        .options(selectinload(AbsenceRequest.student))
        .order_by(AbsenceRequest.created_at.desc())
    )
    if effective_school_id:
        query = query.filter(Student.school_id == effective_school_id)
    if status_filter:
        query = query.filter(AbsenceRequest.status == status_filter.strip().upper())

    rows = (await db.execute(query.limit(100))).scalars().all()
    return [
        AbsenceReasonOut(
            id=r.id,
            student_id=r.student_id,
            student_name=r.student.full_name if r.student else None,
            class_name=r.student.class_name if r.student else None,
            school_id=r.student.school_id if r.student else None,
            parent_id=r.parent_id,
            reason=r.reason,
            absence_date=r.absence_date,
            document_url=r.document_url,
            status=r.status,
            reviewed_by=r.reviewed_by,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.patch("/absence-reasons/{req_id}", summary="Sababli arizani tasdiqlash yoki rad etish")
async def update_absence_status(
    req_id: str,
    request: Request,
    payload: AbsenceStatusUpdate,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    res = await db.execute(
        select(AbsenceRequest)
        .options(selectinload(AbsenceRequest.student))
        .filter(AbsenceRequest.id == req_id)
    )
    req_obj = res.scalar_one_or_none()
    if not req_obj:
        raise HTTPException(status_code=404, detail="Ariza topilmadi")

    if (
        get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value
        and req_obj.student
        and req_obj.student.school_id != current_user.school_id
    ):
        raise HTTPException(status_code=403, detail="Boshqa maktab arizasini boshqarish taqiqlangan.")

    req_obj.status = payload.status
    req_obj.reviewed_by = current_user.username
    await record_audit(
        db,
        user=current_user,
        action="ABSENCE_STATUS_UPDATE",
        target_type="ABSENCE_REQUEST",
        target_id=req_obj.id,
        details=f"Ariza holati: {payload.status}",
        request=request,
    )
    await db.commit()
    return {"id": req_obj.id, "status": req_obj.status, "reviewed_by": req_obj.reviewed_by}
