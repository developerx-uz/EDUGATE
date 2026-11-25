import csv
import io
from datetime import datetime, date, timedelta
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings, get_local_now
from app.core.database import get_db
from app.models.absence import AbsenceRequest
from app.models.school import School
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.device import Device
from app.models.lead import LeadOrder
from app.models.parent import Parent
from app.models.attendance import AttendanceLog, AttendanceEventType, AttendanceStatus
from app.models.audit import AuditLog
from app.models.setting import SystemSetting
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.api.deps import get_current_user, require_superadmin, require_not_read_only
from app.schemas.parent_order import SystemSettingsOut, SystemSettingsUpdate
from app.schemas.school import SchoolUpdate
from app.schemas.student import StudentUpdate
from app.services.audit_service import record_audit, get_role_str
from app.services.settings_service import get_effective_settings

router = APIRouter()


class SchoolAccountSetRequest(BaseModel):
    username: str
    password: Optional[str] = None
    full_name: Optional[str] = None


def _girl_sql_expr():
    safe_pinfl = func.coalesce(Student.pinfl, "")
    safe_gender = func.coalesce(Student.gender, "")
    return (
        (safe_gender == "F")
        | (
            (safe_gender == "")
            & (
                safe_pinfl.like("4%")
                | safe_pinfl.like("6%")
                | (
                    (~safe_pinfl.like("3%"))
                    & (~safe_pinfl.like("5%"))
                    & (Student.last_name.ilike("%va") | Student.last_name.ilike("%qizi"))
                )
            )
        )
    )


def _csv_safe(val: Any) -> str:
    if val is None or val == "":
        return "-"
    s = str(val)
    if s != "-" and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + s
    return s


async def _get_aggregated_stats(db: AsyncSession, school_id: Optional[str] = None) -> dict:
    now = get_local_now()
    today_start = datetime.combine(now.date(), datetime.min.time())
    online_cutoff = now - timedelta(seconds=settings.DEVICE_OFFLINE_SECONDS)

    if school_id:
        schools_count = 1
    else:
        schools_count = (await db.execute(select(func.count(School.id)))).scalar() or 0

    girl_expr = _girl_sql_expr()
    st_stmt = select(
        func.count(Student.id),
        func.coalesce(func.sum(case((girl_expr, 1), else_=0)), 0),
    ).filter(Student.is_active == True)
    if school_id:
        st_stmt = st_stmt.filter(Student.school_id == school_id)
    st_row = (await db.execute(st_stmt)).one()
    students_count = int(st_row[0] or 0)
    girls_count = int(st_row[1] or 0)
    boys_count = max(0, students_count - girls_count)

    tc_stmt = select(func.count(Teacher.id)).filter(Teacher.is_active == True)
    if school_id:
        tc_stmt = tc_stmt.filter(Teacher.school_id == school_id)
    teachers_count = int((await db.execute(tc_stmt)).scalar() or 0)

    dev_stmt = select(
        func.count(Device.id),
        func.coalesce(
            func.sum(
                case(
                    ((Device.last_heartbeat.is_not(None)) & (Device.last_heartbeat >= online_cutoff), 1),
                    else_=0,
                )
            ),
            0,
        ),
    ).filter(Device.is_active == True)
    if school_id:
        dev_stmt = dev_stmt.filter(Device.school_id == school_id)
    dev_row = (await db.execute(dev_stmt)).one()
    devices_count = int(dev_row[0] or 0)
    online_devices_count = int(dev_row[1] or 0)

    if school_id:
        parents_count = int(
            (
                await db.execute(
                    select(func.count(func.distinct(Parent.id)))
                    .join(Parent.students)
                    .filter(Student.school_id == school_id)
                )
            ).scalar()
            or 0
        )
    else:
        parents_count = int((await db.execute(select(func.count(Parent.id)))).scalar() or 0)

    log_stmt = select(
        func.count(AttendanceLog.id),
        func.coalesce(func.sum(case((AttendanceLog.event_type == AttendanceEventType.ENTRY, 1), else_=0)), 0),
        func.coalesce(func.sum(case((AttendanceLog.event_type == AttendanceEventType.EXIT, 1), else_=0)), 0),
        func.coalesce(func.sum(case((AttendanceLog.status == AttendanceStatus.LATE, 1), else_=0)), 0),
        func.coalesce(
            func.sum(
                case(
                    (
                        (AttendanceLog.event_type == AttendanceEventType.ENTRY)
                        & (AttendanceLog.status == AttendanceStatus.ON_TIME),
                        1,
                    ),
                    else_=0,
                )
            ),
            0,
        ),
        func.coalesce(func.sum(case((AttendanceLog.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)), 0),
        func.count(
            func.distinct(
                case(
                    (AttendanceLog.event_type == AttendanceEventType.ENTRY, AttendanceLog.student_id),
                    else_=None,
                )
            )
        ),
    ).filter(AttendanceLog.event_time >= today_start)
    if school_id:
        log_stmt = log_stmt.join(AttendanceLog.student).filter(Student.school_id == school_id)

    l_row = (await db.execute(log_stmt)).one()
    total_today_events = int(l_row[0] or 0)
    today_entries = int(l_row[1] or 0)
    today_exits = int(l_row[2] or 0)
    today_lates = int(l_row[3] or 0)
    today_ontime = int(l_row[4] or 0)
    today_early_leaves = int(l_row[5] or 0)
    unique_present_today = int(l_row[6] or 0)

    return {
        "schools_count": schools_count,
        "students_count": students_count,
        "boys_count": boys_count,
        "girls_count": girls_count,
        "teachers_count": teachers_count,
        "devices_count": devices_count,
        "online_devices_count": online_devices_count,
        "parents_count": parents_count,
        "today_entries": today_entries,
        "today_exits": today_exits,
        "today_lates": today_lates,
        "today_ontime": today_ontime,
        "today_early_leaves": today_early_leaves,
        "unique_present_today": unique_present_today,
        "_total_today_events": total_today_events,
    }


@router.get("/stats", summary="Dashboard Asosiy Statistikasi (Rolga moslashgan)")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    sc_id = current_user.school_id if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value else None
    stats = await _get_aggregated_stats(db, sc_id)
    stats.pop("_total_today_events", None)
    return stats


@router.get("/realtime/pulse", summary="Real-time 1s Auto-Refresh Pulse & State Delta")
async def get_realtime_pulse(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    now = get_local_now()
    today_start = datetime.combine(now.date(), datetime.min.time())
    is_school = get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value
    sc_id = current_user.school_id if is_school else None

    stats = await _get_aggregated_stats(db, sc_id)
    total_today_events = stats.pop("_total_today_events", 0)

    logs_query = (
        select(AttendanceLog)
        .join(AttendanceLog.student)
        .options(
            selectinload(AttendanceLog.student).selectinload(Student.school),
            selectinload(AttendanceLog.device),
        )
        .filter(AttendanceLog.event_time >= today_start)
        .order_by(AttendanceLog.event_time.desc())
        .limit(25)
    )
    if sc_id:
        logs_query = logs_query.filter(Student.school_id == sc_id)

    logs = (await db.execute(logs_query)).scalars().all()
    serialized_logs = []
    for l in logs:
        st = l.student
        serialized_logs.append({
            "id": l.id,
            "student_id": l.student_id,
            "student_name": st.full_name if st else "Noma'lum",
            "student_code": st.student_code if st else "",
            "school_id": st.school_id if st else None,
            "school_name": st.school.name if (st and st.school) else None,
            "device_name": l.device.name if l.device else "Turniket",
            "class_name": st.class_name if st else "",
            "event_type": l.event_type.value if hasattr(l.event_type, "value") else str(l.event_type),
            "status": l.status.value if hasattr(l.status, "value") else str(l.status),
            "confidence": l.confidence,
            "event_time": l.event_time.isoformat() if l.event_time else "",
            "snapshot_path": l.snapshot_path,
            "is_notified": l.is_notified,
        })

    latest_log_id = serialized_logs[0]["id"] if serialized_logs else "none"
    version_hash = (
        f"{stats['schools_count']}_{stats['students_count']}_{stats['teachers_count']}_"
        f"{stats['devices_count']}_{stats['online_devices_count']}_{stats['parents_count']}_"
        f"{total_today_events}_{stats['today_lates']}_{latest_log_id}"
    )

    return {
        "status": "ok",
        "server_time": now.isoformat(),
        "stats": stats,
        "today_logs": serialized_logs,
        "counts": {
            "schools": stats["schools_count"],
            "students": stats["students_count"],
            "teachers": stats["teachers_count"],
            "devices": stats["devices_count"],
            "online_devices": stats["online_devices_count"],
            "parents": stats["parents_count"],
            "logs": total_today_events,
        },
        "version_hash": version_hash,
    }


@router.get("/stats/weekly", summary="Haftalik Davomat Statistikasi (Rolga moslashgan)")
async def get_weekly_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    today = get_local_now().date()
    start_date = today - timedelta(days=6)
    range_start = datetime.combine(start_date, datetime.min.time())
    range_end = datetime.combine(today, datetime.max.time())

    is_school = get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value
    sc_id = current_user.school_id if is_school else None

    query = select(AttendanceLog.event_time, AttendanceLog.status).filter(
        AttendanceLog.event_time >= range_start,
        AttendanceLog.event_time <= range_end,
        AttendanceLog.event_type == AttendanceEventType.ENTRY,
    )
    if sc_id:
        query = query.join(AttendanceLog.student).filter(Student.school_id == sc_id)

    rows = (await db.execute(query)).all()
    buckets = {}
    for ev_time, st_status in rows:
        if not ev_time:
            continue
        d_key = ev_time.date()
        b = buckets.setdefault(d_key, {"on_time": 0, "late": 0})
        if st_status == AttendanceStatus.LATE:
            b["late"] += 1
        elif st_status == AttendanceStatus.ON_TIME:
            b["on_time"] += 1

    day_names = ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan", "Yak"]
    days_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        b = buckets.get(d, {"on_time": 0, "late": 0})
        days_data.append({
            "date": d.strftime("%Y-%m-%d"),
            "day_name": day_names[d.weekday()],
            "on_time": b["on_time"],
            "late": b["late"],
            "total": b["on_time"] + b["late"],
        })
    return days_data


@router.get("/reports/summary", summary="Kunlik/Haftalik/Oylik Tahliliy Hisobot")
async def get_reports_summary(
    period: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    today = get_local_now().date()
    if period == "daily":
        start_d = today
    elif period == "weekly":
        start_d = today - timedelta(days=6)
    else:
        start_d = today.replace(day=1)

    start_dt = datetime.combine(start_d, datetime.min.time())
    sc_id = current_user.school_id if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value else None

    st_q = select(func.count(Student.id)).filter(Student.is_active == True)
    if sc_id:
        st_q = st_q.filter(Student.school_id == sc_id)
    total_students = int((await db.execute(st_q)).scalar() or 0)

    log_q = select(
        func.coalesce(func.sum(case((AttendanceLog.event_type == AttendanceEventType.ENTRY, 1), else_=0)), 0),
        func.coalesce(func.sum(case((AttendanceLog.event_type == AttendanceEventType.EXIT, 1), else_=0)), 0),
        func.coalesce(
            func.sum(
                case(
                    ((AttendanceLog.event_type == AttendanceEventType.ENTRY) & (AttendanceLog.status == AttendanceStatus.ON_TIME), 1),
                    else_=0,
                )
            ),
            0,
        ),
        func.coalesce(func.sum(case((AttendanceLog.status == AttendanceStatus.LATE, 1), else_=0)), 0),
        func.coalesce(func.sum(case((AttendanceLog.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)), 0),
        func.count(
            func.distinct(
                case((AttendanceLog.event_type == AttendanceEventType.ENTRY, AttendanceLog.student_id), else_=None)
            )
        ),
    ).filter(AttendanceLog.event_time >= start_dt)
    if sc_id:
        log_q = log_q.join(AttendanceLog.student).filter(Student.school_id == sc_id)

    row = (await db.execute(log_q)).one()
    entries = int(row[0] or 0)
    exits = int(row[1] or 0)
    on_time = int(row[2] or 0)
    late = int(row[3] or 0)
    early_leave = int(row[4] or 0)
    unique_students = int(row[5] or 0)
    attendance_rate = round((unique_students / total_students) * 100, 1) if total_students > 0 else 0.0

    return {
        "period": period,
        "start_date": start_d.isoformat(),
        "end_date": today.isoformat(),
        "total_students": total_students,
        "unique_students_attended": unique_students,
        "attendance_rate": min(100.0, attendance_rate),
        "entries": entries,
        "exits": exits,
        "on_time": on_time,
        "late": late,
        "early_leave": early_leave,
    }


@router.get("/reports/export-csv", summary="Haqiqiy Davomat va O'quvchilar Hisoboti (CSV)")
async def export_attendance_report_csv(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "O'quvchi ID",
        "F.I.SH",
        "Maktab",
        "Sinf",
        "Jinsi",
        "O'quvchi Kodi",
        "RFID",
        "JSHSHIR",
        "Yuz ID",
        "Hodisalar Soni",
        "Holati",
    ])

    logs_count_subq = (
        select(AttendanceLog.student_id, func.count(AttendanceLog.id).label("cnt"))
        .group_by(AttendanceLog.student_id)
        .subquery()
    )

    query = (
        select(Student, func.coalesce(logs_count_subq.c.cnt, 0))
        .outerjoin(logs_count_subq, Student.id == logs_count_subq.c.student_id)
        .options(selectinload(Student.school))
        .filter(Student.is_active == True)
    )
    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value:
        query = query.filter(Student.school_id == current_user.school_id)

    query = query.order_by(Student.class_name.asc(), Student.last_name.asc())
    rows = (await db.execute(query)).all()

    for st, logs_count in rows:
        school_name = st.school.name if st.school else "-"
        has_face = "Ha" if (st.face_encoding or st.photo_path) else "Yo'q"
        gender_label = "Qiz" if st.inferred_gender == "F" else "O'g'il"

        writer.writerow([
            _csv_safe(st.id),
            _csv_safe(st.full_name),
            _csv_safe(school_name),
            _csv_safe(st.class_name),
            gender_label,
            _csv_safe(st.student_code),
            _csv_safe(st.rfid_card_id),
            _csv_safe(st.pinfl),
            has_face,
            int(logs_count or 0),
            "Faol" if st.is_active else "Nofaol",
        ])

    await record_audit(
        db,
        user=current_user,
        action="REPORT_EXPORT_CSV",
        target_type="REPORT",
        details=f"CSV hisobot yuklab olindi ({len(rows)} ta o'quvchi)",
        request=request,
    )
    await db.commit()

    csv_data = output.getvalue()
    filename = f"edugate_davomat_{get_local_now().date().strftime('%Y_%m_%d')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/schools/detailed", summary="Maktablar ro'yxati va statistikasi (N+1 siz)")
async def get_schools_detailed(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value:
        schools = (
            await db.execute(select(School).filter(School.id == current_user.school_id))
        ).scalars().all()
    else:
        schools = (await db.execute(select(School).order_by(School.created_at.desc()))).scalars().all()

    if not schools:
        return []

    school_ids = [s.id for s in schools]
    today_start = datetime.combine(get_local_now().date(), datetime.min.time())

    # Aggregate students and classes per school
    st_rows = (
        await db.execute(
            select(Student.school_id, Student.class_name, func.count(Student.id))
            .filter(Student.school_id.in_(school_ids), Student.is_active == True)
            .group_by(Student.school_id, Student.class_name)
        )
    ).all()
    student_counts = {}
    classes_map = {}
    for sid, cls_name, cnt in st_rows:
        student_counts[sid] = student_counts.get(sid, 0) + int(cnt or 0)
        if cls_name:
            classes_map.setdefault(sid, set()).add(cls_name)

    # Teachers per school
    tc_rows = (
        await db.execute(
            select(Teacher.school_id, func.count(Teacher.id))
            .filter(Teacher.school_id.in_(school_ids), Teacher.is_active == True)
            .group_by(Teacher.school_id)
        )
    ).all()
    teacher_counts = {sid: int(cnt or 0) for sid, cnt in tc_rows}

    # Devices per school
    dev_rows = (
        await db.execute(
            select(Device.school_id, func.count(Device.id))
            .filter(Device.school_id.in_(school_ids), Device.is_active == True)
            .group_by(Device.school_id)
        )
    ).all()
    device_counts = {sid: int(cnt or 0) for sid, cnt in dev_rows}

    # Today's unique attended students per school
    att_rows = (
        await db.execute(
            select(Student.school_id, func.count(func.distinct(AttendanceLog.student_id)))
            .join(AttendanceLog.student)
            .filter(
                Student.school_id.in_(school_ids),
                AttendanceLog.event_time >= today_start,
                AttendanceLog.event_type == AttendanceEventType.ENTRY,
            )
            .group_by(Student.school_id)
        )
    ).all()
    present_counts = {sid: int(cnt or 0) for sid, cnt in att_rows}

    # School Admin logins (1 school = 1 login)
    user_rows = (
        await db.execute(
            select(User).filter(User.school_id.in_(school_ids), User.role == UserRole.SCHOOL_ADMIN)
        )
    ).scalars().all()
    admin_map = {u.school_id: u for u in user_rows}

    output = []
    for sc in schools:
        st_cnt = student_counts.get(sc.id, 0)
        pres_cnt = present_counts.get(sc.id, 0)
        rate = round((pres_cnt / st_cnt) * 100, 1) if st_cnt > 0 else 0.0
        classes_set = sorted(classes_map.get(sc.id, set()))
        admin_u = admin_map.get(sc.id)

        output.append({
            "id": sc.id,
            "name": sc.name,
            "code": sc.code,
            "address": sc.address,
            "phone": sc.phone,
            "admin_username": admin_u.username if admin_u else None,
            "admin_full_name": admin_u.full_name if admin_u else None,
            "has_login": bool(admin_u),
            "students_count": st_cnt,
            "present_today_count": pres_cnt,
            "attendance_rate": min(100.0, rate),
            "teachers_count": teacher_counts.get(sc.id, 0),
            "devices_count": device_counts.get(sc.id, 0),
            "classes_count": len(classes_set),
            "classes": classes_set,
            "created_at": sc.created_at,
        })

    return output


@router.get("/schools/{school_id}/classes", summary="Maktabdagi sinflar va statistikasi")
async def get_school_classes(
    school_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value and current_user.school_id != school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab sinflarini ko'rish taqiqlangan.")

    students = (
        await db.execute(select(Student).filter(Student.school_id == school_id, Student.is_active == True))
    ).scalars().all()

    class_student_counts = {}
    for st in students:
        if st.class_name:
            class_student_counts[st.class_name] = class_student_counts.get(st.class_name, 0) + 1

    teachers = (
        await db.execute(select(Teacher).filter(Teacher.school_id == school_id, Teacher.is_active == True))
    ).scalars().all()
    class_teachers = {tc.class_name: tc.full_name for tc in teachers if tc.class_name}

    all_class_names = sorted(set(class_student_counts.keys()) | set(class_teachers.keys()))
    return [
        {
            "class_name": cls,
            "students_count": class_student_counts.get(cls, 0),
            "teacher_name": class_teachers.get(cls, "Sinf rahbari kiritilmagan"),
        }
        for cls in all_class_names
    ]


@router.get("/schools/{school_id}/account", summary="Maktabning yagona loginini ko'rish (Faqat Superadmin)")
async def get_school_account(
    school_id: str,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    user = (
        await db.execute(select(User).filter(User.school_id == school_id, User.role == UserRole.SCHOOL_ADMIN))
    ).scalar_one_or_none()
    if not user:
        return {"has_account": False, "school_id": school_id}
    return {
        "has_account": True,
        "school_id": school_id,
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.post("/schools/{school_id}/account", summary="Maktab yagona loginini yaratish yoki yangilash (1 maktab = 1 login)")
async def set_school_account(
    school_id: str,
    request: Request,
    payload: SchoolAccountSetRequest,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    school = (await db.execute(select(School).filter(School.id == school_id))).scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Maktab topilmadi")

    username = payload.username.strip().lower()
    if not username:
        raise HTTPException(status_code=400, detail="Foydalanuvchi nomi kiritilishi shart")

    existing_school_user = (
        await db.execute(select(User).filter(User.school_id == school_id, User.role == UserRole.SCHOOL_ADMIN))
    ).scalar_one_or_none()

    if existing_school_user:
        if existing_school_user.username != username:
            chk = (
                await db.execute(
                    select(User).filter(User.username == username, User.id != existing_school_user.id)
                )
            ).scalar_one_or_none()
            if chk:
                raise HTTPException(status_code=400, detail=f"'{username}' foydalanuvchi nomi allaqachon band.")
            existing_school_user.username = username

        if payload.password and payload.password.strip():
            if len(payload.password.strip()) < 6:
                raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgidan iborat bo'lishi kerak")
            existing_school_user.hashed_password = get_password_hash(payload.password.strip())
        if payload.full_name:
            existing_school_user.full_name = payload.full_name.strip()

        await record_audit(
            db,
            user=current_user,
            action="SCHOOL_ACCOUNT_UPDATE",
            target_type="SCHOOL",
            target_id=school_id,
            details=f"{school.name} logini yangilandi (@{existing_school_user.username})",
            request=request,
        )
        await db.commit()
        await db.refresh(existing_school_user)
        return {
            "message": "Maktab logini va paroli muvaffaqiyatli yangilandi (1 maktab = 1 login)",
            "username": existing_school_user.username,
            "school_id": school_id,
        }

    chk = (await db.execute(select(User).filter(User.username == username))).scalar_one_or_none()
    if chk:
        raise HTTPException(status_code=400, detail=f"'{username}' foydalanuvchi nomi allaqachon band.")

    if not payload.password or len(payload.password.strip()) < 6:
        raise HTTPException(status_code=400, detail="Parol kamida 6 ta belgidan iborat bo'lishi kerak")

    new_user = User(
        school_id=school_id,
        username=username,
        full_name=payload.full_name.strip() if payload.full_name else f"{school.name} Ma'muri",
        email=f"{username}@edugate.uz",
        hashed_password=get_password_hash(payload.password.strip()),
        role=UserRole.SCHOOL_ADMIN,
        is_superadmin=False,
        is_active=True,
    )
    db.add(new_user)
    await record_audit(
        db,
        user=current_user,
        action="SCHOOL_ACCOUNT_CREATE",
        target_type="SCHOOL",
        target_id=school_id,
        details=f"{school.name} uchun login yaratildi (@{username})",
        request=request,
    )
    await db.commit()
    return {
        "message": "Maktab uchun yagona login muvaffaqiyatli yaratildi (1 maktab = 1 login)",
        "username": new_user.username,
        "school_id": school_id,
    }


@router.get("/students/all", summary="Barcha o'quvchilar (Boshqaruv uchun)")
async def get_all_students(
    school_id: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    effective_school_id = (
        current_user.school_id if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value else school_id
    )

    query = select(Student).options(selectinload(Student.school)).filter(Student.is_active == True)
    if effective_school_id:
        query = query.filter(Student.school_id == effective_school_id)
    if class_name:
        query = query.filter(Student.class_name == class_name)

    students = (await db.execute(query.order_by(Student.created_at.desc()))).scalars().all()
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
            "pinfl": st.pinfl,
            "gender": st.inferred_gender,
            "rfid_card_id": st.rfid_card_id,
            "photo_path": st.photo_path,
            "has_face_encoding": bool(st.face_encoding or st.photo_path),
            "is_active": st.is_active,
            "created_at": st.created_at,
        }
        for st in students
    ]


@router.get("/devices/all", summary="Barcha qurilmalar va kameralar")
async def get_all_devices(
    school_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    effective_school_id = (
        current_user.school_id if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value else school_id
    )
    now = get_local_now()

    query = select(Device).options(selectinload(Device.school))
    if effective_school_id:
        query = query.filter(Device.school_id == effective_school_id)

    devices = (await db.execute(query.order_by(Device.created_at.desc()))).scalars().all()
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
            "is_online": bool(
                dev.is_active
                and dev.last_heartbeat
                and (now - dev.last_heartbeat).total_seconds() <= settings.DEVICE_OFFLINE_SECONDS
            ),
            "last_heartbeat": dev.last_heartbeat,
            "created_at": dev.created_at,
        }
        for dev in devices
    ]


@router.get("/parents", summary="Ota-onalar ro'yxati va Telegram Status")
async def get_parents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    query = select(Parent).options(selectinload(Parent.students)).order_by(Parent.created_at.desc())
    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value:
        query = query.join(Parent.students).filter(Student.school_id == current_user.school_id).distinct()

    parents = (await db.execute(query)).scalars().all()
    return [
        {
            "id": p.id,
            "phone_number": p.phone_number,
            "telegram_chat_id": p.telegram_chat_id,
            "is_verified": p.is_verified,
            "full_name": p.full_name,
            "students": [s.full_name for s in p.students],
            "created_at": p.created_at,
        }
        for p in parents
    ]


@router.delete("/students/{student_id}", summary="O'quvchini o'chirish")
async def delete_student(
    student_id: str,
    request: Request,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    student = (await db.execute(select(Student).filter(Student.id == student_id))).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value and student.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab o'quvchisini o'chirish taqiqlangan.")

    st_name = student.full_name
    await db.delete(student)
    await record_audit(
        db,
        user=current_user,
        action="STUDENT_DELETE",
        target_type="STUDENT",
        target_id=student_id,
        details=f"{st_name} o'chirildi",
        request=request,
    )
    await db.commit()
    return {"message": "O'quvchi muvaffaqiyatli o'chirildi"}


@router.delete("/devices/{device_id}", summary="Qurilmani o'chirish")
async def delete_device(
    device_id: str,
    request: Request,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    device = (await db.execute(select(Device).filter(Device.id == device_id))).scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Qurilma topilmadi")

    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value and device.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab qurilmasini o'chirish taqiqlangan.")

    dev_name = device.name
    await db.delete(device)
    await record_audit(
        db,
        user=current_user,
        action="DEVICE_DELETE",
        target_type="DEVICE",
        target_id=device_id,
        details=f"{dev_name} qurilmasi o'chirildi",
        request=request,
    )
    await db.commit()
    return {"message": "Qurilma muvaffaqiyatli o'chirildi"}


@router.delete("/schools/{school_id}", summary="Maktabni o'chirish (Faqat Superadmin)")
async def delete_school(
    school_id: str,
    request: Request,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    school = (await db.execute(select(School).filter(School.id == school_id))).scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Maktab topilmadi")

    sc_name = school.name
    await db.delete(school)
    await record_audit(
        db,
        user=current_user,
        action="SCHOOL_DELETE",
        target_type="SCHOOL",
        target_id=school_id,
        details=f"{sc_name} maktabi o'chirildi",
        request=request,
    )
    await db.commit()
    return {"message": "Maktab muvaffaqiyatli o'chirildi"}


@router.put("/students/{student_id}", summary="O'quvchini tahrirlash")
async def update_student(
    student_id: str,
    request: Request,
    payload: dict,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    student = (await db.execute(select(Student).filter(Student.id == student_id))).scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value:
        if student.school_id != current_user.school_id:
            raise HTTPException(status_code=403, detail="Boshqa maktab o'quvchisini tahrirlash huquqi mavjud emas.")
        payload.pop("school_id", None)

    if "student_code" in payload and payload["student_code"]:
        new_code = str(payload["student_code"]).strip()
        if new_code != student.student_code:
            dup = (
                await db.execute(select(Student.id).filter(Student.student_code == new_code, Student.id != student.id))
            ).scalar_one_or_none()
            if dup:
                raise HTTPException(status_code=400, detail=f"'{new_code}' o'quvchi kodi band.")

    for field in ["first_name", "last_name", "class_name", "student_code", "pinfl", "birth_cert_number", "rfid_card_id", "gender"]:
        if field in payload and payload[field] is not None:
            val = payload[field]
            setattr(student, field, val.strip() if isinstance(val, str) else val)

    if get_role_str(current_user) == UserRole.SUPERADMIN.value and payload.get("school_id"):
        student.school_id = payload["school_id"]

    await record_audit(
        db,
        user=current_user,
        action="STUDENT_UPDATE",
        target_type="STUDENT",
        target_id=student.id,
        details=f"{student.full_name} ma'lumotlari yangilandi",
        request=request,
    )
    await db.commit()
    await db.refresh(student)
    return {
        "message": "O'quvchi ma'lumotlari muvaffaqiyatli yangilandi",
        "student": {
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "class_name": student.class_name,
            "student_code": student.student_code,
        },
    }


@router.put("/schools/{school_id}", summary="Maktabni tahrirlash (Faqat Superadmin)")
async def update_school(
    school_id: str,
    request: Request,
    payload: dict,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    school = (await db.execute(select(School).filter(School.id == school_id))).scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Maktab topilmadi")

    if payload.get("code") and payload["code"].strip() != school.code:
        dup = (
            await db.execute(select(School.id).filter(School.code == payload["code"].strip(), School.id != school.id))
        ).scalar_one_or_none()
        if dup:
            raise HTTPException(status_code=400, detail=f"'{payload['code']}' kodi allaqachon band.")

    for field in ["name", "code", "address", "phone"]:
        if field in payload and payload[field] is not None:
            setattr(school, field, str(payload[field]).strip())

    await record_audit(
        db,
        user=current_user,
        action="SCHOOL_UPDATE",
        target_type="SCHOOL",
        target_id=school.id,
        details=f"{school.name} yangilandi",
        request=request,
    )
    await db.commit()
    await db.refresh(school)
    return {"message": "Maktab muvaffaqiyatli yangilandi", "school": {"id": school.id, "name": school.name, "code": school.code}}


@router.get("/notifications", summary="Jonli Tizim Bildirishnomalari")
async def get_admin_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    now = get_local_now()
    today_start = datetime.combine(now.date(), datetime.min.time())
    online_cutoff = now - timedelta(seconds=settings.DEVICE_OFFLINE_SECONDS)
    role_str = get_role_str(current_user)
    sc_id = current_user.school_id if role_str == UserRole.SCHOOL_ADMIN.value else None

    items = []

    # 1. Bugungi kechikishlar
    late_q = (
        select(AttendanceLog)
        .join(AttendanceLog.student)
        .options(selectinload(AttendanceLog.student))
        .filter(AttendanceLog.event_time >= today_start, AttendanceLog.status == AttendanceStatus.LATE)
        .order_by(AttendanceLog.event_time.desc())
        .limit(8)
    )
    if sc_id:
        late_q = late_q.filter(Student.school_id == sc_id)
    for l in (await db.execute(late_q)).scalars().all():
        items.append({
            "id": f"late_{l.id}",
            "type": "late",
            "icon": "fa-clock",
            "color": "text-amber-400",
            "text": f"{l.student.full_name if l.student else 'O\'quvchi'} ({l.student.class_name if l.student else ''}) darsga kechikib keldi",
            "time": l.event_time.strftime("%H:%M:%S"),
        })

    # 2. Sababli arizalar (PENDING)
    abs_q = (
        select(AbsenceRequest)
        .join(AbsenceRequest.student)
        .options(selectinload(AbsenceRequest.student))
        .filter(AbsenceRequest.status == "PENDING")
        .order_by(AbsenceRequest.created_at.desc())
        .limit(5)
    )
    if sc_id:
        abs_q = abs_q.filter(Student.school_id == sc_id)
    for r in (await db.execute(abs_q)).scalars().all():
        items.append({
            "id": f"abs_{r.id}",
            "type": "absence",
            "icon": "fa-file-medical",
            "color": "text-sky-400",
            "text": f"Sababli ariza: {r.student.full_name if r.student else ''} — {r.reason[:60]}",
            "time": r.created_at.strftime("%d.%m %H:%M"),
        })

    # 3. Aloqasiz qurilmalar
    dev_q = select(Device).filter(
        Device.is_active == True,
        (Device.last_heartbeat.is_(None)) | (Device.last_heartbeat < online_cutoff),
    ).limit(5)
    if sc_id:
        dev_q = dev_q.filter(Device.school_id == sc_id)
    for d in (await db.execute(dev_q)).scalars().all():
        items.append({
            "id": f"dev_{d.id}",
            "type": "device",
            "icon": "fa-video-slash",
            "color": "text-rose-400",
            "text": f"Qurilma signali kutilmoqda: {d.name}",
            "time": d.last_heartbeat.strftime("%d.%m %H:%M") if d.last_heartbeat else "Hali ulanmagan",
        })

    # 4. Yangi arizalar (Faqat Superadmin / Monitoring)
    if role_str != UserRole.SCHOOL_ADMIN.value:
        leads = (
            await db.execute(
                select(LeadOrder).filter(LeadOrder.status == "NEW").order_by(LeadOrder.created_at.desc()).limit(5)
            )
        ).scalars().all()
        for ld in leads:
            items.append({
                "id": f"lead_{ld.id}",
                "type": "lead",
                "icon": "fa-paper-plane",
                "color": "text-emerald-400",
                "text": f"Yangi ariza: {ld.full_name} ({ld.school_info or ld.phone})",
                "time": ld.created_at.strftime("%d.%m %H:%M"),
            })

    return items


@router.get("/audit-logs", summary="Tizim Audit Jurnali")
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value:
        query = query.filter(AuditLog.school_id == current_user.school_id)

    rows = (await db.execute(query)).scalars().all()
    return [
        {
            "id": a.id,
            "username": a.username,
            "role": a.role,
            "action": a.action,
            "target_type": a.target_type,
            "details": a.details,
            "ip_address": a.ip_address,
            "created_at": a.created_at.isoformat() if a.created_at else "",
        }
        for a in rows
    ]


@router.get("/settings", response_model=SystemSettingsOut, summary="Tizim sozlamalarini olish")
async def get_system_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    sc_id = current_user.school_id if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value else None
    eff = await get_effective_settings(db, sc_id)
    return SystemSettingsOut(
        school_start_time=eff.school_start_time,
        late_threshold_minutes=eff.late_threshold_minutes,
        school_end_time=eff.school_end_time,
        debounce_minutes=eff.debounce_minutes,
        language=eff.language,
        admin_chat_id=eff.admin_chat_id,
        notify_late=eff.notify_late,
        notify_entry=eff.notify_entry,
        notify_exit=eff.notify_exit,
        bot_token_configured=eff.bot_token_configured,
    )


@router.put("/settings", response_model=SystemSettingsOut, summary="Tizim sozlamalarini saqlash")
async def update_system_settings(
    request: Request,
    payload: SystemSettingsUpdate,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    role_str = get_role_str(current_user)
    sc_id = current_user.school_id if role_str == UserRole.SCHOOL_ADMIN.value else None

    if sc_id:
        row = (await db.execute(select(SystemSetting).filter(SystemSetting.school_id == sc_id))).scalar_one_or_none()
    else:
        row = (await db.execute(select(SystemSetting).filter(SystemSetting.school_id.is_(None)))).scalar_one_or_none()

    if not row:
        row = SystemSetting(school_id=sc_id)
        db.add(row)

    for field, val in payload.model_dump(exclude_unset=True).items():
        if field == "admin_chat_id" and role_str == UserRole.SCHOOL_ADMIN.value:
            continue  # Global admin chat faqat superadmin uchun
        setattr(row, field, val)

    await record_audit(
        db,
        user=current_user,
        action="SETTINGS_UPDATE",
        target_type="SETTINGS",
        target_id=sc_id or "global",
        details="Tizim va bildirishnoma sozlamalari yangilandi",
        request=request,
    )
    await db.commit()

    eff = await get_effective_settings(db, sc_id)
    return SystemSettingsOut(
        school_start_time=eff.school_start_time,
        late_threshold_minutes=eff.late_threshold_minutes,
        school_end_time=eff.school_end_time,
        debounce_minutes=eff.debounce_minutes,
        language=eff.language,
        admin_chat_id=eff.admin_chat_id,
        notify_late=eff.notify_late,
        notify_entry=eff.notify_entry,
        notify_exit=eff.notify_exit,
        bot_token_configured=eff.bot_token_configured,
    )
