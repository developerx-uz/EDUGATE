import random
import csv
import io
from datetime import datetime, date, timedelta
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
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
from app.core.security import generate_device_token

router = APIRouter()


@router.get("/stats", summary="Superadmin Dashboard Asosiy Statistikasi")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
) -> Any:
    today_start = datetime.combine(date.today(), datetime.min.time())

    schools_count = (await db.execute(select(func.count(School.id)))).scalar() or 0
    students_count = (await db.execute(select(func.count(Student.id)))).scalar() or 0
    teachers_count = (await db.execute(select(func.count(Teacher.id)))).scalar() or 0
    devices_count = (await db.execute(select(func.count(Device.id)))).scalar() or 0
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
        "teachers_count": teachers_count,
        "devices_count": devices_count,
        "parents_count": parents_count,
        "today_entries": today_entries,
        "today_exits": today_exits,
        "today_lates": today_lates,
        "today_ontime": today_ontime
    }


@router.get("/stats/weekly", summary="Haftalik Davomat Haqiqiy Statistikasi")
async def get_weekly_stats(
    db: AsyncSession = Depends(get_db)
) -> Any:
    today = date.today()
    days_data = []

    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())

        result = await db.execute(
            select(AttendanceLog).filter(
                AttendanceLog.event_time >= day_start,
                AttendanceLog.event_time <= day_end
            )
        )
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


@router.get("/reports/export-csv", summary="Haqiqiy Davomat va O'quvchilar Hisoboti (CSV)")
async def export_attendance_report_csv(
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
        .order_by(Student.class_name.asc(), Student.last_name.asc())
    )
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
    db: AsyncSession = Depends(get_db)
) -> Any:
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

        output.append({
            "id": sc.id,
            "name": sc.name,
            "code": sc.code,
            "address": sc.address,
            "phone": sc.phone,
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
    db: AsyncSession = Depends(get_db)
) -> Any:
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


@router.get("/students/all", summary="Barcha o'quvchilar (Boshqaruv uchun)")
async def get_all_students(
    school_id: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Any:
    query = select(Student).options(selectinload(Student.school))
    if school_id:
        query = query.filter(Student.school_id == school_id)
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
    db: AsyncSession = Depends(get_db)
) -> Any:
    query = select(Device).options(selectinload(Device.school))
    if school_id:
        query = query.filter(Device.school_id == school_id)

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
    db: AsyncSession = Depends(get_db)
) -> Any:
    query = select(Parent).options(selectinload(Parent.students)).order_by(Parent.created_at.desc())
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
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    await db.delete(student)
    await db.commit()
    return {"message": "O'quvchi muvaffaqiyatli o'chirildi"}


@router.delete("/devices/{device_id}", summary="Qurilmani o'chirish")
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Qurilma topilmadi")

    await db.delete(device)
    await db.commit()
    return {"message": "Qurilma muvaffaqiyatli o'chirildi"}


@router.delete("/schools/{school_id}", summary="Maktabni o'chirish")
async def delete_school(
    school_id: str,
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
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    for field in ["first_name", "last_name", "class_name", "student_code", "pinfl", "rfid_card_id", "school_id"]:
        if field in payload and payload[field] is not None:
            setattr(student, field, payload[field])

    await db.commit()
    await db.refresh(student)
    return {"message": "O'quvchi ma'lumotlari muvaffaqiyatli yangilandi", "student": {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "class_name": student.class_name,
        "student_code": student.student_code
    }}


@router.put("/schools/{school_id}", summary="Maktabni tahrirlash")
async def update_school(
    school_id: str,
    payload: dict,
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

