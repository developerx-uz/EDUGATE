from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings, get_local_now
from app.core.database import get_db
from app.core.security import generate_device_token
from app.models.device import Device
from app.models.school import School
from app.models.user import User, UserRole
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceHeartbeatRequest, DeviceOut
from app.api.deps import get_current_user, get_current_device, require_not_read_only
from app.services.audit_service import record_audit

router = APIRouter()


def is_device_online(dev: Device) -> bool:
    if not dev.is_active or not dev.last_heartbeat:
        return False
    age = (get_local_now() - dev.last_heartbeat).total_seconds()
    return age <= settings.DEVICE_OFFLINE_SECONDS


def serialize_device(dev: Device, school_name: Optional[str] = None) -> dict:
    return {
        "id": dev.id,
        "school_id": dev.school_id,
        "school_name": school_name or (dev.school.name if getattr(dev, "school", None) else "Noma'lum"),
        "name": dev.name,
        "device_token": dev.device_token,
        "device_type": dev.device_type,
        "direction": dev.direction,
        "ip_address": dev.ip_address,
        "location_description": dev.location_description,
        "is_active": dev.is_active,
        "is_online": is_device_online(dev),
        "last_heartbeat": dev.last_heartbeat,
        "created_at": dev.created_at,
    }


@router.post("/", response_model=DeviceOut, status_code=status.HTTP_201_CREATED, summary="Yangi kamera/turniketni ro'yxatdan o'tkazish")
async def create_device(
    request: Request,
    device_in: DeviceCreate,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
):
    effective_school_id = (
        current_user.school_id
        if current_user.role == UserRole.SCHOOL_ADMIN
        else (device_in.school_id or current_user.school_id)
    )
    if not effective_school_id:
        raise HTTPException(status_code=400, detail="Maktab tanlanishi shart")

    school = (
        await db.execute(select(School).filter(School.id == effective_school_id))
    ).scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Tanlangan maktab topilmadi")

    token = generate_device_token()
    device = Device(
        school_id=effective_school_id,
        name=device_in.name.strip(),
        device_token=token,
        device_type=device_in.device_type,
        direction=device_in.direction,
        ip_address=device_in.ip_address.strip() if device_in.ip_address else None,
        location_description=device_in.location_description.strip() if device_in.location_description else None,
    )
    db.add(device)
    await db.flush()
    await record_audit(
        db,
        user=current_user,
        action="DEVICE_CREATE",
        target_type="DEVICE",
        target_id=device.id,
        details=f"{device.name} ({device.device_type.value}) qo'shildi",
        request=request,
    )
    await db.commit()
    await db.refresh(device)
    return serialize_device(device, school.name)


@router.get("/", response_model=List[DeviceOut], summary="Barcha kameralar va qurilmalar ro'yxati")
async def list_devices(
    school_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    effective_school_id = (
        current_user.school_id
        if current_user.role == UserRole.SCHOOL_ADMIN
        else (school_id or current_user.school_id)
    )
    query = select(Device).options(selectinload(Device.school))
    if effective_school_id:
        query = query.filter(Device.school_id == effective_school_id)
    result = await db.execute(query.order_by(Device.created_at.desc()))
    return [serialize_device(d) for d in result.scalars().all()]


@router.put("/{device_id}", response_model=DeviceOut, summary="Qurilma sozlamalarini tahrirlash")
async def update_device(
    device_id: str,
    request: Request,
    payload: DeviceUpdate,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Device).options(selectinload(Device.school)).filter(Device.id == device_id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Qurilma topilmadi")

    if current_user.role == UserRole.SCHOOL_ADMIN and device.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab qurilmasini tahrirlash taqiqlangan.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(device, field, val.strip() if isinstance(val, str) else val)

    await record_audit(
        db,
        user=current_user,
        action="DEVICE_UPDATE",
        target_type="DEVICE",
        target_id=device.id,
        details=f"{device.name} yangilandi (is_active={device.is_active})",
        request=request,
    )
    await db.commit()
    await db.refresh(device)
    return serialize_device(device)


@router.post("/heartbeat", summary="Kamera/Turniket jonli aloqa (Heartbeat) signali")
async def device_heartbeat(
    payload: DeviceHeartbeatRequest = DeviceHeartbeatRequest(),
    device: Device = Depends(get_current_device),
    db: AsyncSession = Depends(get_db),
):
    now_local = get_local_now()
    device.last_heartbeat = now_local
    if payload.ip_address:
        device.ip_address = payload.ip_address.strip()
    await db.commit()
    return {
        "status": "ok",
        "device_id": device.id,
        "device_name": device.name,
        "last_heartbeat": now_local.isoformat(),
    }
