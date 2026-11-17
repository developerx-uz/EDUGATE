import random
import csv
import io
from datetime import datetime, date, timedelta
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.school import School
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.device import Device, DeviceType, DeviceDirection
from app.models.parent import Parent
from app.models.attendance import AttendanceLog, AttendanceEventType, AttendanceStatus
from app.models.user import User, UserRole
from app.core.security import generate_device_token, get_password_hash
from app.api.deps import get_current_user, require_superadmin, require_not_read_only

router = APIRouter()


class SchoolAccountSetRequest(BaseModel):
    username: str
    password: Optional[str] = None
    full_name: Optional[str] = None


@router.get("/stats", summary="Dashboard Asosiy Statistikasi (Rolga moslashgan)")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    today_start = datetime.combine(date.today(), datetime.min.time())

    if current_user.role == UserRole.SCHOOL_ADMIN:
        sc_id = current_user.school_id
        schools_count = 1
        students_count = (await db.execute(select(func.count(Student.id)).filter(Student.school_id == sc_id, Student.is_active == True))).scalar() or 0
        girls_count = (await db.execute(
            select(func.count(Student.id)).filter(
                Student.school_id == sc_id,
                Student.is_active == True,
                (Student.last_name.ilike('%va') | Student.last_name.ilike('%qizi') | Student.pinfl.like('4%') | Student.pinfl.like('6%'))
            )
        )).scalar() or 0
        boys_count = max(0, students_count - girls_count)
        teachers_count = (await db.execute(select(func.count(Teacher.id)).filter(Teacher.school_id == sc_id, Teacher.is_active == True))).scalar() or 0
        devices_count = (await db.execute(select(func.count(Device.id)).filter(Device.school_id == sc_id, Device.is_active == True))).scalar() or 0
        
        parents_count = (await db.execute(
            select(func.count(func.distinct(Parent.id)))
            .join(Parent.students)
            .filter(Student.school_id == sc_id)
        )).scalar() or 0

        today_logs = (await db.execute(
            select(AttendanceLog)
            .join(AttendanceLog.student)
            .filter(Student.school_id == sc_id, AttendanceLog.event_time >= today_start)
        )).scalars().all()
    else:
        schools_count = (await db.execute(select(func.count(School.id)))).scalar() or 0
        students_count = (await db.execute(select(func.count(Student.id)).filter(Student.is_active == True))).scalar() or 0
        girls_count = (await db.execute(
            select(func.count(Student.id)).filter(
                Student.is_active == True,
                (Student.last_name.ilike('%va') | Student.last_name.ilike('%qizi') | Student.pinfl.like('4%') | Student.pinfl.like('6%'))
            )
        )).scalar() or 0
        boys_count = max(0, students_count - girls_count)
        teachers_count = (await db.execute(select(func.count(Teacher.id)).filter(Teacher.is_active == True))).scalar() or 0
        devices_count = (await db.execute(select(func.count(Device.id)).filter(Device.is_active == True))).scalar() or 0
        parents_count = (await db.execute(select(func.count(Parent.id)))).scalar() or 0

        today_logs = (await db.execute(
            select(AttendanceLog).filter(AttendanceLog.event_time >= today_start)
        )).scalars().all()

    today_entries = sum(1 for log in today_logs if log.event_type == AttendanceEventType.ENTRY)
    today_exits = sum(1 for log in today_logs if log.event_type == AttendanceEventType.EXIT)
    today_lates = sum(1 for log in today_logs if log.status == AttendanceStatus.LATE)
    today_ontime = sum(1 for log in today_logs if log.status == AttendanceStatus.ON_TIME)

    return {
        "schools_count": schools_count,
        "students_count": students_count,
        "boys_count": boys_count,
        "girls_count": girls_count,
        "teachers_count": teachers_count,
        "devices_count": devices_count,
        "parents_count": parents_count,
        "today_entries": today_entries,
        "today_exits": today_exits,
        "today_lates": today_lates,
        "today_ontime": today_ontime
    }


@router.get("/realtime/pulse", summary="Real-time 1s Auto-Refresh Pulse & State Delta (Rolga moslashgan)")
async def get_realtime_pulse(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    now = datetime.now()
    today_start = datetime.combine(now.date(), datetime.min.time())

    is_school = current_user.role == UserRole.SCHOOL_ADMIN
    sc_id = current_user.school_id if is_school else None

    if is_school:
        schools_count = 1
        students_count = (await db.execute(select(func.count(Student.id)).filter(Student.school_id == sc_id, Student.is_active == True))).scalar() or 0
        teachers_count = (await db.execute(select(func.count(Teacher.id)).filter(Teacher.school_id == sc_id, Teacher.is_active == True))).scalar() or 0
        devices_count = (await db.execute(select(func.count(Device.id)).filter(Device.school_id == sc_id, Device.is_active == True))).scalar() or 0
        parents_count = (await db.execute(
            select(func.count(func.distinct(Parent.id)))
            .join(Parent.students)
            .filter(Student.school_id == sc_id)
        )).scalar() or 0

        today_events_res = await db.execute(
            select(AttendanceLog.event_type, AttendanceLog.status)
            .join(AttendanceLog.student)
            .filter(Student.school_id == sc_id, AttendanceLog.event_time >= today_start)
        )
        today_events = today_events_res.all()

        logs_res = await db.execute(
            select(AttendanceLog)
            .options(selectinload(AttendanceLog.student), selectinload(AttendanceLog.device))
            .join(AttendanceLog.student)
            .filter(Student.school_id == sc_id, AttendanceLog.event_time >= today_start)
            .order_by(AttendanceLog.event_time.desc())
            .limit(25)
        )
        logs = logs_res.scalars().all()
    else:
        schools_count = (await db.execute(select(func.count(School.id)))).scalar() or 0
        students_count = (await db.execute(select(func.count(Student.id)).filter(Student.is_active == True))).scalar() or 0
        teachers_count = (await db.execute(select(func.count(Teacher.id)).filter(Teacher.is_active == True))).scalar() or 0
        devices_count = (await db.execute(select(func.count(Device.id)).filter(Device.is_active == True))).scalar() or 0
        parents_count = (await db.execute(select(func.count(Parent.id)))).scalar() or 0

        today_events_res = await db.execute(
            select(AttendanceLog.event_type, AttendanceLog.status)
            .filter(AttendanceLog.event_time >= today_start)
        )
        today_events = today_events_res.all()

        logs_res = await db.execute(
            select(AttendanceLog)
            .options(selectinload(AttendanceLog.student), selectinload(AttendanceLog.device))
            .filter(AttendanceLog.event_time >= today_start)
            .order_by(AttendanceLog.event_time.desc())
            .limit(25)
        )
        logs = logs_res.scalars().all()

    today_entries = sum(1 for et, _ in today_events if et == AttendanceEventType.ENTRY)
    today_exits = sum(1 for et, _ in today_events if et == AttendanceEventType.EXIT)
    today_lates = sum(1 for _, st in today_events if st == AttendanceStatus.LATE)
    today_ontime = sum(1 for _, st in today_events if st == AttendanceStatus.ON_TIME)

    serialized_logs = []
    for l in logs:
        st_name = l.student.full_name if l.student else "Noma'lum"
        st_code = l.student.student_code if l.student else ""
        cls_name = l.student.class_name if l.student else ""
        serialized_logs.append({
            "id": l.id,
            "student_id": l.student_id,
            "student_name": st_name,
            "student_code": st_code,
            "class_name": cls_name,
            "event_type": l.event_type.value if hasattr(l.event_type, "value") else str(l.event_type),
            "status": l.status.value if hasattr(l.status, "value") else str(l.status),
            "confidence": l.confidence,
            "event_time": l.event_time.isoformat() if l.event_time else "",
            "is_notified": l.is_notified
        })

    version_hash = f"{schools_count}_{students_count}_{teachers_count}_{devices_count}_{parents_count}_{len(today_events)}"

    return {
        "status": "ok",
        "server_time": now.isoformat(),
        "stats": {
            "schools_count": schools_count,
            "students_count": students_count,
            "teachers_count": teachers_count,
            "devices_count": devices_count,
            "parents_count": parents_count,
            "today_entries": today_entries,
            "today_exits": today_exits,
            "today_lates": today_lates,
            "today_ontime": today_ontime
        },
        "today_logs": serialized_logs,
        "counts": {
            "schools": schools_count,
            "students": students_count,
            "teachers": teachers_count,
            "devices": devices_count,
            "parents": parents_count,
            "logs": len(today_events)
        },
        "version_hash": version_hash
    }


@router.get("/stats/weekly", summary="Haftalik Davomat Statistikasi (Rolga moslashgan)")
async def get_weekly_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    today = date.today()
    days_data = []
    is_school = current_user.role == UserRole.SCHOOL_ADMIN
    sc_id = current_user.school_id if is_school else None

    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())

        query = select(AttendanceLog).filter(
            AttendanceLog.event_time >= day_start,
            AttendanceLog.event_time <= day_end
        )
        if is_school:
            query = query.join(AttendanceLog.student).filter(Student.school_id == sc_id)

        result = await db.execute(query)
        logs = result.scalars().all()

        ontime = sum(1 for l in logs if l.status == AttendanceStatus.ON_TIME and l.event_type == AttendanceEventType.ENTRY)
        late = sum(1 for l in logs if l.status == AttendanceStatus.LATE and l.event_type == AttendanceEventType.ENTRY)
        total = ontime + late

        days_data.append({
            "date": day_date.strftime("%Y-%m-%d"),
            "day_name": ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan", "Yak"][day_date.weekday()],
            "on_time": ontime,
            "late": late,
            "total": total
        })

    return days_data

    return days_data


@router.get("/reports/export-csv", summary="Haqiqiy Davomat va O'quvchilar Hisoboti (CSV)")
async def export_attendance_report_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    output = io.StringIO()
    # UTF-8 BOM for Excel compatibility in Uzbekistan/Russian locales
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=';')

    writer.writerow([
        "O'quvchi ID",
        "F.I.SH",
        "Maktab",
        "Sinf",
        "O'quvchi Kodi",
        "RFID",
        "JSHSHIR",
        "Yuz ID",
        "Hodisalar Soni",
        "Holati"
    ])

    query = (
        select(Student)
        .options(selectinload(Student.school), selectinload(Student.attendance_logs))
        .filter(Student.is_active == True)
    )
    if current_user.role == UserRole.SCHOOL_ADMIN:
        query = query.filter(Student.school_id == current_user.school_id)

    query = query.order_by(Student.class_name.asc(), Student.last_name.asc())
    result = await db.execute(query)
    students = result.scalars().all()

    for st in students:
        school_name = st.school.name if st.school else "-"
        logs_count = len(st.attendance_logs) if st.attendance_logs else 0
        has_face = "Ha" if (st.face_encoding or st.photo_path) else "Yo'q"

        writer.writerow([
            st.id,
            st.full_name,
            school_name,
            st.class_name or "-",
            st.student_code,
            st.rfid_card_id or "-",
            st.pinfl or "-",
            has_face,
            logs_count,
            "Faol" if st.is_active else "Nofaol"
        ])

    csv_data = output.getvalue()
    filename = f"edugate_davomat_{date.today().strftime('%Y_%m_%d')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/schools/detailed", summary="Maktablar ro'yxati va statistikasi")
async def get_schools_detailed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if current_user.role == UserRole.SCHOOL_ADMIN:
        result = await db.execute(select(School).filter(School.id == current_user.school_id))
    else:
        result = await db.execute(select(School).order_by(School.created_at.desc()))
    schools = result.scalars().all()

    output = []
    for sc in schools:
        res_st = await db.execute(select(Student).filter(Student.school_id == sc.id, Student.is_active == True))
        students = res_st.scalars().all()
        classes_set = sorted(list(set(st.class_name for st in students if st.class_name)))

        res_tc = await db.execute(select(Teacher).filter(Teacher.school_id == sc.id, Teacher.is_active == True))
        teachers = res_tc.scalars().all()

        res_dev = await db.execute(select(Device).filter(Device.school_id == sc.id, Device.is_active == True))
        devices = res_dev.scalars().all()

        # Maktabning yagona login hisobi (1 maktab = 1 login)
        res_u = await db.execute(select(User).filter(User.school_id == sc.id, User.role == UserRole.SCHOOL_ADMIN))
        school_admin_user = res_u.scalar_one_or_none()

        output.append({
            "id": sc.id,
            "name": sc.name,
            "code": sc.code,
            "address": sc.address,
            "phone": sc.phone,
            "admin_username": school_admin_user.username if school_admin_user else None,
            "admin_full_name": school_admin_user.full_name if school_admin_user else None,
            "has_login": bool(school_admin_user),
            "students_count": len(students),
            "teachers_count": len(teachers),
            "devices_count": len(devices),
            "classes_count": len(classes_set),
            "classes": classes_set,
            "created_at": sc.created_at
        })

    return output


@router.get("/schools/{school_id}/classes", summary="Maktabdagi sinflar va statistikasi")
async def get_school_classes(
    school_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if current_user.role == UserRole.SCHOOL_ADMIN and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab sinflarini ko'rish taqiqlangan.")

    res_st = await db.execute(select(Student).filter(Student.school_id == school_id, Student.is_active == True))
    students = res_st.scalars().all()

    class_student_counts = {}
    for st in students:
        if st.class_name:
            class_student_counts[st.class_name] = class_student_counts.get(st.class_name, 0) + 1

    res_tc = await db.execute(select(Teacher).filter(Teacher.school_id == school_id, Teacher.is_active == True))
    teachers = res_tc.scalars().all()
    class_teachers = {}
    for tc in teachers:
        if tc.class_name:
            class_teachers[tc.class_name] = tc.full_name

    all_class_names = sorted(list(set(list(class_student_counts.keys()) + list(class_teachers.keys()))))

    classes_list = []
    for cls in all_class_names:
        classes_list.append({
            "class_name": cls,
            "students_count": class_student_counts.get(cls, 0),
            "teacher_name": class_teachers.get(cls, "Sinf rahbari kiritilmagan")
        })

    return classes_list


@router.get("/schools/{school_id}/account", summary="Maktabning yagona loginini ko'rish (Faqat Superadmin)")
async def get_school_account(
    school_id: str,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    res = await db.execute(select(User).filter(User.school_id == school_id, User.role == UserRole.SCHOOL_ADMIN))
    user = res.scalar_one_or_none()
    if not user:
        return {"has_account": False, "school_id": school_id}
    return {
        "has_account": True,
        "school_id": school_id,
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


@router.post("/schools/{school_id}/account", summary="Maktab yagona loginini yaratish yoki parolini yangilash (1 maktab = 1 login)")
async def set_school_account(
    school_id: str,
    payload: SchoolAccountSetRequest,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    res_sc = await db.execute(select(School).filter(School.id == school_id))
    school = res_sc.scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Maktab topilmadi")

    username = payload.username.strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomi kiritilishi shart")

    # Qoida: 1 maktab = 1 login (2-login mumkin emas)
    res_user = await db.execute(select(User).filter(User.school_id == school_id, User.role == UserRole.SCHOOL_ADMIN))
    existing_school_user = res_user.scalar_one_or_none()

    if existing_school_user:
        # Username o'zgartirilayotgan bo'lsa, boshqa foydalanuvchida yo'qligini tekshirish
        if existing_school_user.username != username:
            chk = (await db.execute(select(User).filter(User.username == username, User.id != existing_school_user.id))).scalar_one_or_none()
            if chk:
                raise HTTPException(status_code=400, detail=f"'{username}' foydalanuvchi nomi allaqachon band.")
            existing_school_user.username = username

        if payload.password and len(payload.password.strip()) >= 6:
            existing_school_user.hashed_password = get_password_hash(payload.password.strip())
        if payload.full_name:
            existing_school_user.full_name = payload.full_name.strip()

        await db.commit()
        await db.refresh(existing_school_user)
        return {
            "message": "Maktab logini va paroli muvaffaqiyatli yangilandi (1 maktab = 1 login)",
            "username": existing_school_user.username,
            "school_id": school_id
        }
    else:
        # Yangi hisob ochish
        chk = (await db.execute(select(User).filter(User.username == username))).scalar_one_or_none()
        if chk:
            raise HTTPException(status_code=400, detail=f"'{username}' foydalanuvchi nomi allaqachon band.")

        if not payload.password or len(payload.password.strip()) < 6:
            raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgidan iborat bo'lishi kerak")

        new_user = User(
            school_id=school_id,
            username=username,
            full_name=payload.full_name or f"{school.name} Ma'muri",
            email=f"{username}@edugate.uz",
            hashed_password=get_password_hash(payload.password.strip()),
            role=UserRole.SCHOOL_ADMIN,
            is_superadmin=False,
            is_active=True
        )
        db.add(new_user)
        await db.commit()
        return {
            "message": "Maktab uchun yagona login muvaffaqiyatli yaratildi (1 maktab = 1 login)",
            "username": new_user.username,
            "school_id": school_id
        }


@router.get("/students/all", summary="Barcha o'quvchilar (Boshqaruv uchun)")
async def get_all_students(
    school_id: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Maktab ma'muri faqat o'z maktabi o'quvchilarini ko'ra oladi
    if current_user.role == UserRole.SCHOOL_ADMIN:
        effective_school_id = current_user.school_id
    else:
        effective_school_id = school_id

    query = select(Student).options(selectinload(Student.school))
    if effective_school_id:
        query = query.filter(Student.school_id == effective_school_id)
    if class_name:
        query = query.filter(Student.class_name == class_name)

    result = await db.execute(query.order_by(Student.created_at.desc()))
    students = result.scalars().all()

    return [
        {
            "id": st.id,
            "school_id": st.school_id,
            "school_name": st.school.name if st.school else "Biriktirilmagan",
            "first_name": st.first_name,
            "last_name": st.last_name,
            "full_name": st.full_name,
            "student_code": st.student_code,
            "class_name": st.class_name,
            "rfid_card_id": st.rfid_card_id,
            "has_face_encoding": bool(st.face_encoding),
            "is_active": st.is_active,
            "created_at": st.created_at
        }
        for st in students
    ]


@router.get("/devices/all", summary="Barcha qurilmalar va kameralar")
async def get_all_devices(
    school_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # 2. Faqat o'zining kameralarini kuzata oladi
    if current_user.role == UserRole.SCHOOL_ADMIN:
        effective_school_id = current_user.school_id
    else:
        effective_school_id = school_id

    query = select(Device).options(selectinload(Device.school))
    if effective_school_id:
        query = query.filter(Device.school_id == effective_school_id)

    result = await db.execute(query.order_by(Device.created_at.desc()))
    devices = result.scalars().all()

    return [
        {
            "id": dev.id,
            "school_id": dev.school_id,
            "school_name": dev.school.name if dev.school else "Noma'lum",
            "name": dev.name,
            "device_token": dev.device_token,
            "device_type": dev.device_type,
            "direction": dev.direction,
            "ip_address": dev.ip_address,
            "location_description": dev.location_description,
            "is_active": dev.is_active,
            "created_at": dev.created_at
        }
        for dev in devices
    ]


@router.get("/parents", summary="Ota-onalar ro'yxati va Telegram Status")
async def get_parents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    query = select(Parent).options(selectinload(Parent.students)).order_by(Parent.created_at.desc())
    if current_user.role == UserRole.SCHOOL_ADMIN:
        query = query.join(Parent.students).filter(Student.school_id == current_user.school_id).distinct()

    result = await db.execute(query)
    parents = result.scalars().all()

    return [
        {
            "id": p.id,
            "phone_number": p.phone_number,
            "telegram_chat_id": p.telegram_chat_id,
            "full_name": p.full_name,
            "students": [s.full_name for s in p.students],
            "created_at": p.created_at
        }
        for p in parents
    ]


@router.delete("/students/{student_id}", summary="O'quvchini o'chirish")
async def delete_student(
    student_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Xalq Ta'limi hech narsani o'chira olmaydi
    if current_user.role == UserRole.MINISTRY_VIEWER:
        raise HTTPException(status_code=403, detail="Xalq Ta'limi portali faqat monitoring (ko'rish) uchun. Ma'lumotlarni o'chirish taqiqlangan.")

    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    # Maktab ma'muri faqat o'z o'quvchisini o'chira oladi
    if current_user.role == UserRole.SCHOOL_ADMIN and student.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab o'quvchisini o'chirish taqiqlangan.")

    await db.delete(student)
    await db.commit()
    return {"message": "O'quvchi muvaffaqiyatli o'chirildi"}


@router.delete("/devices/{device_id}", summary="Qurilmani o'chirish")
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if current_user.role == UserRole.MINISTRY_VIEWER:
        raise HTTPException(status_code=403, detail="Xalq Ta'limi portali faqat monitoring (ko'rish) uchun. Qurilmani o'chirish taqiqlangan.")

    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Qurilma topilmadi")

    if current_user.role == UserRole.SCHOOL_ADMIN and device.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab qurilmasini o'chirish taqiqlangan.")

    await db.delete(device)
    await db.commit()
    return {"message": "Qurilma muvaffaqiyatli o'chirildi"}


@router.delete("/schools/{school_id}", summary="Maktabni o'chirish (Faqat Superadmin)")
async def delete_school(
    school_id: str,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(School).filter(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Maktab topilmadi")

    await db.delete(school)
    await db.commit()
    return {"message": "Maktab muvaffaqiyatli o'chirildi"}


@router.put("/students/{student_id}", summary="O'quvchini tahrirlash")
async def update_student(
    student_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if current_user.role == UserRole.MINISTRY_VIEWER:
        raise HTTPException(status_code=403, detail="Xalq Ta'limi portali faqat monitoring (ko'rish) uchun. O'quvchini tahrirlash taqiqlangan.")

    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    if current_user.role == UserRole.SCHOOL_ADMIN:
        if student.school_id != current_user.school_id:
            raise HTTPException(status_code=403, detail="Boshqa maktab o'quvchisini tahrirlash huquqi mavjud emas.")
        payload.pop("school_id", None)

    for field in ["first_name", "last_name", "class_name", "student_code", "pinfl", "rfid_card_id"]:
        if field in payload and payload[field] is not None:
            setattr(student, field, payload[field])

    if current_user.role == UserRole.SUPERADMIN and "school_id" in payload and payload["school_id"]:
        student.school_id = payload["school_id"]

    await db.commit()
    await db.refresh(student)
    return {"message": "O'quvchi ma'lumotlari muvaffaqiyatli yangilandi", "student": {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "class_name": student.class_name,
        "student_code": student.student_code
    }}


@router.put("/schools/{school_id}", summary="Maktabni tahrirlash (Faqat Superadmin)")
async def update_school(
    school_id: str,
    payload: dict,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(School).filter(School.id == school_id))
    school = result.scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Maktab topilmadi")

    for field in ["name", "code", "address", "phone"]:
        if field in payload and payload[field] is not None:
            setattr(school, field, payload[field])

    await db.commit()
    await db.refresh(school)
    return {"message": "Maktab muvaffaqiyatli yangilandi", "school": {
        "id": school.id,
        "name": school.name,
        "code": school.code
    }}

