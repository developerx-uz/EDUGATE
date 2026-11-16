from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.models.school import School
from app.schemas.user import Token, UserOut, LoginRequest, ProfileUpdateRequest, PasswordChangeRequest
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token, summary="Tizimga kirish (Superadmin, Xalq Ta'limi, Maktab)")
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

    role_str = str(user.role.value if hasattr(user.role, 'value') else user.role)
    school_name = None
    if user.school_id:
        res_s = await db.execute(select(School).filter(School.id == user.school_id))
        s_obj = res_s.scalar_one_or_none()
        if s_obj:
            school_name = s_obj.name

    access_token = create_access_token(data={
        "sub": user.username,
        "role": role_str,
        "school_id": user.school_id
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role_str,
        "full_name": user.full_name or user.username,
        "school_id": user.school_id,
        "school_name": school_name
    }


@router.post("/login-json", response_model=Token, summary="Tizimga kirish (JSON formatda)")
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

    role_str = str(user.role.value if hasattr(user.role, 'value') else user.role)
    school_name = None
    if user.school_id:
        res_s = await db.execute(select(School).filter(School.id == user.school_id))
        s_obj = res_s.scalar_one_or_none()
        if s_obj:
            school_name = s_obj.name

    access_token = create_access_token(data={
        "sub": user.username,
        "role": role_str,
        "school_id": user.school_id
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role_str,
        "full_name": user.full_name or user.username,
        "school_id": user.school_id,
        "school_name": school_name
    }


@router.get("/me", response_model=UserOut, summary="Joriy foydalanuvchi ma'lumotlari")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    school_name = None
    if current_user.school_id:
        res_s = await db.execute(select(School).filter(School.id == current_user.school_id))
        s_obj = res_s.scalar_one_or_none()
        if s_obj:
            school_name = s_obj.name

    role_str = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": role_str,
        "school_id": current_user.school_id,
        "school_name": school_name,
        "is_superadmin": current_user.is_superadmin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }


@router.put("/profile", response_model=UserOut, summary="Profil ma'lumotlarini yangilash")
async def update_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if data.full_name is not None:
        current_user.full_name = data.full_name.strip()
    if data.email is not None:
        current_user.email = data.email.strip()
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/change-password", summary="Parolni xavfsiz o'zgartirish")
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hozirgi amaldagi parol noto'g'ri kiritildi."
        )
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yangi parol kamida 6 ta belgidan iborat bo'lishi kerak."
        )
    current_user.hashed_password = get_password_hash(data.new_password)
    await db.commit()
    return {"status": "ok", "message": "Parol muvaffaqiyatli yangilandi."}

