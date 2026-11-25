from datetime import time
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
from app.core.config import get_local_now, to_local_naive
from app.services.image_utils import save_base64_image
from app.services.notifier import notifier
from app.services.settings_service import get_effective_settings

logger = logging.getLogger("edugate.attendance")


def _parse_hhmm(value: str, fallback: time) -> time:
    try:
        hour, minute = map(int, value.split(":"))
        return time(hour, minute)
    except Exception:
        return fallback


class AttendanceService:
    @staticmethod
    async def process_event(
        db: AsyncSession,
        event: AttendanceEventCreate,
        device: Device,
        background_tasks: BackgroundTasks
    ) -> AttendanceEventResponse:
        now_local = get_local_now()

        # Qurilma tirikligini qayd etish (Heartbeat)
        if device is not None:
            device.last_heartbeat = now_local

        # 1. O'quvchini aniqlash (ID, Kod yoki RFID karta orqali)
        query = (
            select(Student)
            .options(selectinload(Student.parents), selectinload(Student.school))
            .filter(Student.is_active == True)
        )
        if event.student_id:
            query = query.filter(Student.id == event.student_id)
        elif event.student_code:
            query = query.filter(Student.student_code == event.student_code.strip())
        elif event.rfid_card_id:
            query = query.filter(Student.rfid_card_id == event.rfid_card_id.strip())
        else:
            await db.commit()
            return AttendanceEventResponse(
                status="ERROR",
                message="O'quvchini aniqlash uchun ma'lumot (ID, kod yoki RFID) topilmadi."
            )

        result = await db.execute(query)
        student = result.scalar_one_or_none()

        if not student:
            await db.commit()
            return AttendanceEventResponse(
                status="NOT_FOUND",
                message="O'quvchi bazadan topilmadi yoki nofaol holatda."
            )

        # Maktab mosligini tekshirish (Boshqa maktab kamerasi o'zga maktab o'quvchisini yoza olmasligi shart)
        if device and device.school_id and student.school_id != device.school_id:
            await db.commit()
            return AttendanceEventResponse(
                status="ERROR",
                message="Xavfsizlik cheklovi: o'quvchi ushbu qurilma biriktirilgan maktabga tegishli emas."
            )

        eff_settings = await get_effective_settings(db, student.school_id)

        # Agar qurilma faqat kirish yoki faqat chiqishga sozlangan bo'lsa, moslash
        effective_event_type = event.event_type
        if device and device.direction == DeviceDirection.IN:
            effective_event_type = AttendanceEventType.ENTRY
        elif device and device.direction == DeviceDirection.OUT:
            effective_event_type = AttendanceEventType.EXIT

        # 2. Yo'nalish bo'yicha Anti-Passback / Debounce (BIDIRECTIONAL kameralarda ENTRY/EXIT alohida)
        direction_key = effective_event_type.value
        is_debounced = await debounce_manager.is_debounced(student.id, direction_key)
        if is_debounced:
            await db.commit()
            return AttendanceEventResponse(
                status="IGNORED_DEBOUNCED",
                message=(
                    f"Takroriy signal inkor qilindi: {student.full_name} oxirgi "
                    f"{eff_settings.debounce_minutes} daqiqada qayd etilgan."
                ),
                is_debounced=True,
                student_name=student.full_name,
                event_type=effective_event_type,
            )

        # 3. Mahalliy vaqt va kechikish/erta ketishni hisoblash
        event_time = to_local_naive(event.event_time) if event.event_time else now_local
        attendance_status = AttendanceStatus.ON_TIME
        is_late = False
        is_early_leave = False

        event_local_time = event_time.time()
        if effective_event_type == AttendanceEventType.ENTRY:
            school_start = _parse_hhmm(eff_settings.school_start_time, time(8, 0))
            if event_local_time > school_start:
                minutes_late = (
                    (event_local_time.hour * 60 + event_local_time.minute)
                    - (school_start.hour * 60 + school_start.minute)
                )
                if minutes_late > eff_settings.late_threshold_minutes:
                    attendance_status = AttendanceStatus.LATE
                    is_late = True
        elif effective_event_type == AttendanceEventType.EXIT:
            school_end = _parse_hhmm(eff_settings.school_end_time, time(14, 0))
            if event_local_time < school_end:
                attendance_status = AttendanceStatus.EARLY_LEAVE
                is_early_leave = True

        # 4. Snapshot rasmni saqlash (agar yuborilgan bo'lsa)
        snapshot_path = None
        if event.snapshot_base64:
            try:
                snapshot_path, _ = save_base64_image(
                    event.snapshot_base64,
                    subfolder="snapshots",
                    filename_prefix=f"snap_{student.student_code}",
                )
            except Exception as snap_err:
                logger.warning(f"Snapshot saqlashda xatolik: {snap_err}")

        # 5. Bazaga yangi log yozish
        log = AttendanceLog(
            student_id=student.id,
            device_id=device.id if device else None,
            event_type=effective_event_type,
            status=attendance_status,
            confidence=event.confidence,
            event_time=event_time,
            snapshot_path=snapshot_path,
            is_notified=False,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)

        # 6. Redis/xotira keshda debounceni faollashtirish
        await debounce_manager.mark_seen(
            student.id,
            direction_key,
            ttl_seconds=max(60, eff_settings.debounce_minutes * 60),
        )

        # 7. Ota-onaga Telegram orqali xabar yuborish (sozlamalarga qarab)
        should_notify = False
        if effective_event_type == AttendanceEventType.ENTRY:
            should_notify = eff_settings.notify_entry or (is_late and eff_settings.notify_late)
        elif effective_event_type == AttendanceEventType.EXIT:
            should_notify = eff_settings.notify_exit

        parent_chat_ids = [p.telegram_chat_id for p in student.parents if p.telegram_chat_id]
        if should_notify and parent_chat_ids:
            background_tasks.add_task(
                notifier.send_attendance_alert,
                chat_ids=parent_chat_ids,
                student_name=student.full_name,
                event_type=effective_event_type.value,
                event_time_str=event_time.strftime("%H:%M:%S"),
                is_late=is_late,
                is_early_leave=is_early_leave,
                school_name=student.school.name if student.school else None,
                log_id=log.id,
            )

        return AttendanceEventResponse(
            status="SUCCESS",
            message=f"{student.full_name} muvaffaqiyatli qayd etildi.",
            is_debounced=False,
            log_id=log.id,
            student_name=student.full_name,
            event_type=log.event_type,
            event_time=log.event_time,
            attendance_status=log.status,
            snapshot_path=log.snapshot_path,
        )
