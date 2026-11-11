from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import generate_device_token
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceOut

router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=status.HTTP_201_CREATED, summary="Yangi kamera/turniketni ro'yxatdan o'tkazish")
async def create_device(
    device_in: DeviceCreate,
    db: AsyncSession = Depends(get_db)
):
    token = generate_device_token()
    device = Device(
        school_id=device_in.school_id,
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
    school_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Device).filter(Device.school_id == school_id))
    return result.scalars().all()
