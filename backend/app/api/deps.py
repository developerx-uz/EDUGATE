from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.config import settings
from app.models.device import Device
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


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


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiya tokeni kiritilmagan."
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token noto'g'ri.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token yaroqsiz yoki muddati o'tgan.")

    result = await db.execute(select(User).filter(User.username == username, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi.")
    return user


async def get_current_superadmin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ushbu amalni bajarish uchun Superadmin huquqi talab qilinadi."
        )
    return current_user
