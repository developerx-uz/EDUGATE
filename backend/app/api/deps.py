from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.device import Device


async def get_current_device(
    x_device_token: Optional[str] = Header(None, alias="X-Device-Token"),
    db: AsyncSession = Depends(get_db)
) -> Device:
    """
    Kamera yoki Turniket qurilmasini xavfsiz token orqali tekshirish
    """
    if not x_device_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Device-Token sarlavhasi (header) majburiy."
        )

    result = await db.execute(select(Device).filter(Device.device_token == x_device_token, Device.is_active == True))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Qurilma tokeni noto'g'ri yoki qurilma o'chirilgan."
        )

    return device

