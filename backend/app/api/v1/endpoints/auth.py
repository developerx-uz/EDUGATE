from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User, UserRole
from app.schemas.user import Token, UserOut, LoginRequest
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token, summary="Hokimlik / Vazirlik Superadmin Login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(User).filter(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi nomi yoki parol noto'g'ri."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi hisobi faol emas."
        )

    access_token = create_access_token(data={"sub": user.username, "role": str(user.role.value if hasattr(user.role, 'value') else user.role)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": str(user.role.value if hasattr(user.role, 'value') else user.role),
        "full_name": user.full_name or "Viloyat / Shahar Hokimligi Superadmini"
    }


@router.post("/login-json", response_model=Token, summary="Hokimlik / Vazirlik Superadmin Login (JSON)")
async def login_json(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(User).filter(User.username == login_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi nomi yoki parol noto'g'ri."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi hisobi faol emas."
        )

    access_token = create_access_token(data={"sub": user.username, "role": str(user.role.value if hasattr(user.role, 'value') else user.role)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": str(user.role.value if hasattr(user.role, 'value') else user.role),
        "full_name": user.full_name or "Viloyat / Shahar Hokimligi Superadmini"
    }


@router.get("/me", response_model=UserOut, summary="Joriy foydalanuvchi ma'lumotlari")
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    return current_user
