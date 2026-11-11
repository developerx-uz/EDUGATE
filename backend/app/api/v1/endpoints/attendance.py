from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_device
from app.models.device import Device
from app.models.attendance import AttendanceLog
from app.models.student import Student
from app.schemas.attendance import AttendanceEventCreate, AttendanceEventResponse, AttendanceLogOut
from app.services.attendance_service import AttendanceService

router = APIRouter()


@router.post("/event", response_model=AttendanceEventResponse, summary="Kamera yoki Turniketdan davomat hodisasini qabul qilish")
async def receive_attendance_event(
    event: AttendanceEventCreate,
    background_tasks: BackgroundTasks,
    device: Device = Depends(get_current_device),
    db: AsyncSession = Depends(get_db)
):
    """
    Ushbu endpoint barcha AI kameralar, Face ID terminallari va turniketlardan keluvchi
    asosiy signal qabul qiluvchi shlyuz hisoblanadi.
    - X-Device-Token orqali qurilma autentifikatsiya qilinadi.
    - Takroriy signallar (debounce) avtomatik filtrlanadi.
    - Ota-onaga Telegram orqali fon rejimida tezkor xabar uzatiladi.
    """
    return await AttendanceService.process_event(
        db=db,
        event=event,
        device=device,
        background_tasks=background_tasks
    )


@router.get("/today", response_model=List[AttendanceLogOut], summary="Bugungi kunlik davomat loglari (Dashboard uchun)")
async def get_today_attendance(
    school_id: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    today_start = datetime.combine(date.today(), datetime.min.time())
    query = (
        select(AttendanceLog)
        .options(selectinload(AttendanceLog.student))
        .filter(AttendanceLog.event_time >= today_start)
        .order_by(AttendanceLog.event_time.desc())
    )

    result = await db.execute(query)
    logs = result.scalars().all()

    output = []
    for log in logs:
        if log.student:
            if school_id and log.student.school_id != school_id:
                continue
            if class_name and log.student.class_name != class_name:
                continue

            output.append(AttendanceLogOut(
                id=log.id,
                student_id=log.student_id,
                student_name=log.student.full_name,
                class_name=log.student.class_name,
                event_type=log.event_type,
                status=log.status,
                event_time=log.event_time,
                confidence=log.confidence,
                is_notified=log.is_notified
            ))

    return output
