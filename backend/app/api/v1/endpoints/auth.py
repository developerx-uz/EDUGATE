from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    needs_password_rehash,
)
from app.models.user import User
from app.models.school import School
from app.schemas.user import Token, UserOut, LoginRequest, ProfileUpdateRequest, PasswordChangeRequest
from app.api.deps import get_current_user
from app.services.audit_service import record_audit, get_role_str

router = APIRouter()


async def _authenticate_user(
    db: AsyncSession, username: str, password: str, request: Request
) -> dict:
    clean_username = username.strip()
    result = await db.execute(select(User).filter(User.username == clean_username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi nomi yoki parol noto'g'ri.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Foydalanuvchi hisobi faol emas.",
        )

    # Transparent upgrade of legacy SHA-256 hashes to bcrypt
    if needs_password_rehash(user.hashed_password):
        user.hashed_password = get_password_hash(password)

    role_str = get_role_str(user)
    school_name = None
    if user.school_id:
        res_s = await db.execute(select(School).filter(School.id == user.school_id))
        s_obj = res_s.scalar_one_or_none()
        if s_obj:
            school_name = s_obj.name

    await record_audit(
        db,
        user=user,
        action="LOGIN",
        target_type="USER",
        target_id=user.id,
        details=f"Tizimga muvaffaqiyatli kirish ({role_str})",
        request=request,
    )
    await db.commit()

    access_token = create_access_token(
        data={"sub": user.username, "role": role_str, "school_id": user.school_id}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": role_str,
        "full_name": user.full_name or user.username,
        "school_id": user.school_id,
        "school_name": school_name,
    }


def _serialize_user(user: User, school_name: str | None) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": get_role_str(user),
        "school_id": user.school_id,
        "school_name": school_name,
        "is_superadmin": user.is_superadmin,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@router.post("/login", response_model=Token, summary="Tizimga kirish (OAuth2 Form)")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await _authenticate_user(db, form_data.username, form_data.password, request)


@router.post("/login-json", response_model=Token, summary="Tizimga kirish (JSON formatda)")
async def login_json(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    return await _authenticate_user(db, login_data.username, login_data.password, request)


@router.get("/me", response_model=UserOut, summary="Joriy foydalanuvchi ma'lumotlari")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    school_name = None
    if current_user.school_id:
        res_s = await db.execute(select(School).filter(School.id == current_user.school_id))
        s_obj = res_s.scalar_one_or_none()
        if s_obj:
            school_name = s_obj.name
    return _serialize_user(current_user, school_name)


@router.put("/profile", response_model=UserOut, summary="Profil ma'lumotlarini yangilash")
async def update_profile(
    request: Request,
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    if data.full_name is not None:
        current_user.full_name = data.full_name.strip()
    if data.email is not None:
        clean_email = data.email.strip() or None
        if clean_email and clean_email != current_user.email:
            dup = (
                await db.execute(
                    select(User).filter(User.email == clean_email, User.id != current_user.id)
                )
            ).scalar_one_or_none()
            if dup:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ushbu elektron pochta boshqa hisobga biriktirilgan.",
                )
        current_user.email = clean_email

    await record_audit(
        db,
        user=current_user,
        action="PROFILE_UPDATE",
        target_type="USER",
        target_id=current_user.id,
        details="Profil ma'lumotlari yangilandi",
        request=request,
    )
    await db.commit()
    await db.refresh(current_user)

    school_name = None
    if current_user.school_id:
        res_s = await db.execute(select(School).filter(School.id == current_user.school_id))
        s_obj = res_s.scalar_one_or_none()
        if s_obj:
            school_name = s_obj.name
    return _serialize_user(current_user, school_name)


@router.put("/change-password", summary="Parolni xavfsiz o'zgartirish")
async def change_password(
    request: Request,
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hozirgi amaldagi parol noto'g'ri kiritildi.",
        )
    if len(data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yangi parol kamida 6 ta belgidan iborat bo'lishi kerak.",
        )
    current_user.hashed_password = get_password_hash(data.new_password)
    await record_audit(
        db,
        user=current_user,
        action="PASSWORD_CHANGE",
        target_type="USER",
        target_id=current_user.id,
        details="Foydalanuvchi paroli yangilandi",
        request=request,
    )
    await db.commit()
    return {"status": "ok", "message": "Parol muvaffaqiyatli yangilandi."}
