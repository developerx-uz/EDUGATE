from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import generate_device_token
from app.models.device import Device
from app.models.user import User, UserRole
from app.schemas.device import DeviceCreate, DeviceOut
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=status.HTTP_201_CREATED, summary="Yangi kamera/turniketni ro'yxatdan o'tkazish")
async def create_device(
    device_in: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == UserRole.MINISTRY_VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Xalq Ta'limi portali faqat monitoring (ko'rish) uchun. Qurilma qo'shish taqiqlangan."
        )

    effective_school_id = current_user.school_id if current_user.role == UserRole.SCHOOL_ADMIN else (device_in.school_id or current_user.school_id)
    if not effective_school_id:
        raise HTTPException(status_code=400, detail="Maktab tanlanishi shart")

    token = generate_device_token()
    device = Device(
        school_id=effective_school_id,
        name=device_in.name,
        device_token=token,
        device_type=device_in.device_type,
        direction=device_in.direction,
        ip_address=device_in.ip_address,
        location_description=device_in.location_description
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.get("/", response_model=List[DeviceOut], summary="Barcha kameralar va qurilmalar ro'yxati")
async def list_devices(
    school_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    effective_school_id = current_user.school_id if current_user.role == UserRole.SCHOOL_ADMIN else (school_id or current_user.school_id)
    query = select(Device)
    if effective_school_id:
        query = query.filter(Device.school_id == effective_school_id)
    result = await db.execute(query)
    return result.scalars().all()

