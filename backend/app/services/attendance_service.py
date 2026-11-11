from datetime import datetime, time
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks

from app.models.student import Student
from app.models.device import Device, DeviceDirection
from app.models.attendance import AttendanceLog, AttendanceEventType, AttendanceStatus
from app.schemas.attendance import AttendanceEventCreate, AttendanceEventResponse
from app.core.redis import debounce_manager
from app.core.config import settings
from app.services.notifier import notifier

logger = logging.getLogger("edugate.attendance")


class AttendanceService:
    @staticmethod
    async def process_event(
        db: AsyncSession,
        event: AttendanceEventCreate,
        device: Device,
        background_tasks: BackgroundTasks
    ) -> AttendanceEventResponse:
        # 1. O'quvchini aniqlash (ID, Kod yoki RFID karta orqali)
        query = select(Student).options(selectinload(Student.parents)).filter(Student.is_active == True)
        if event.student_id:
            query = query.filter(Student.id == event.student_id)
        elif event.student_code:
            query = query.filter(Student.student_code == event.student_code)
        elif event.rfid_card_id:
            query = query.filter(Student.rfid_card_id == event.rfid_card_id)
        else:
            return AttendanceEventResponse(
                status="ERROR",
                message="O'quvchini aniqlash uchun ma'lumot (ID, kod yoki RFID) topilmadi."
            )

        result = await db.execute(query)
        student = result.scalar_one_or_none()

        if not student:
            return AttendanceEventResponse(
                status="NOT_FOUND",
                message="O'quvchi bazadan topilmadi yoki nofaol holatda."
            )

        # 2. Yo'nalishni aniqlash (Kameraning sozlamasiga qarab)
        direction_key = device.direction.value if device else event.event_type.value

        # 3. ANTI-PASSBACK & DEBOUNCE TEKSHIRUVI
        is_debounced = await debounce_manager.is_debounced(student.id, direction_key)
        if is_debounced:
            return AttendanceEventResponse(
                status="IGNORED_DEBOUNCED",
                message=f"Takroriy signal inkor qilindi: {student.full_name} oxirgi {settings.DEBOUNCE_MINUTES} daqiqada qayd etilgan.",
                is_debounced=True,
                student_name=student.full_name
            )

        # 4. Kechikishni hisoblash (Faqat kirish paytida)
        event_time = event.event_time or datetime.utcnow()
        attendance_status = AttendanceStatus.ON_TIME
        is_late = False

        if event.event_type == AttendanceEventType.ENTRY:
            try:
                start_hour, start_min = map(int, settings.SCHOOL_START_TIME.split(":"))
                school_start = time(start_hour, start_min)
                # Dars boshlanishidan + LATE_THRESHOLD_MINUTES keyin kelgan bo'lsa
                event_local_time = event_time.time()
                if event_local_time > school_start:
                    minutes_late = (event_local_time.hour * 60 + event_local_time.minute) - (start_hour * 60 + start_min)
                    if minutes_late > settings.LATE_THRESHOLD_MINUTES:
                        attendance_status = AttendanceStatus.LATE
                        is_late = True
            except Exception as e:
                logger.warning(f"Vaqtni hisoblashda xatolik: {e}")

        # 5. Bazaga yangi log yozish
        log = AttendanceLog(
            student_id=student.id,
            device_id=device.id if device else None,
            event_type=event.event_type,
            status=attendance_status,
            confidence=event.confidence,
            event_time=event_time,
            is_notified=False
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)

        # 6. Redis'da debounceni faollashtirish
        await debounce_manager.mark_seen(student.id, direction_key, ttl_seconds=settings.DEBOUNCE_MINUTES * 60)

        # 7. Ota-onaga Telegram orqali xabar yuborish (Background Task orqali)
        parent_chat_ids = [p.telegram_chat_id for p in student.parents if p.telegram_chat_id]
        if parent_chat_ids:
            background_tasks.add_task(
                notifier.send_attendance_alert,
                chat_ids=parent_chat_ids,
                student_name=student.full_name,
                event_type=event.event_type.value,
                event_time_str=event_time.strftime("%H:%M:%S"),
                is_late=is_late
            )

        return AttendanceEventResponse(
            status="SUCCESS",
            message=f"{student.full_name} muvaffaqiyatli qayd etildi.",
            is_debounced=False,
            log_id=log.id,
            student_name=student.full_name,
            event_type=log.event_type,
            event_time=log.event_time,
            attendance_status=log.status
        )
