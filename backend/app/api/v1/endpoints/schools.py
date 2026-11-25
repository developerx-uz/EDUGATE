from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.school import School
from app.models.user import User, UserRole
from app.schemas.school import SchoolCreate, SchoolOut
from app.api.deps import get_current_user, require_superadmin
from app.services.audit_service import record_audit

router = APIRouter()


@router.post(
    "/",
    response_model=SchoolOut,
    status_code=status.HTTP_201_CREATED,
    summary="Yangi maktab va uning yagona loginini yaratish (Faqat Superadmin)",
)
async def create_school(
    request: Request,
    school_in: SchoolCreate,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    code_clean = school_in.code.strip()
    existing_school = (
        await db.execute(select(School).filter(School.code == code_clean))
    ).scalar_one_or_none()
    if existing_school:
        raise HTTPException(
            status_code=400, detail=f"'{code_clean}' kodli maktab allaqachon mavjud."
        )

    school = School(
        name=school_in.name.strip(),
        code=code_clean,
        address=school_in.address.strip() if school_in.address else None,
        phone=school_in.phone.strip() if school_in.phone else None,
        settings=school_in.settings or {},
    )
    db.add(school)
    await db.flush()

    # 1 maktab = 1 login qat'iy talabi (yagona tranzaksiya ichida)
    username = (school_in.admin_username or f"maktab_{school.code.lower()}").strip().lower()
    raw_password = (school_in.admin_password or f"Maktab_{school.code}2026!").strip()
    if len(raw_password) < 6:
        raise HTTPException(
            status_code=400, detail="Maktab logini paroli kamida 6 ta belgidan iborat bo'lishi kerak."
        )

    existing_user = (
        await db.execute(select(User).filter(User.username == username))
    ).scalar_one_or_none()
    if existing_user:
        username = f"maktab_{school.code.lower()}_{school.id[:4]}"

    school_admin = User(
        school_id=school.id,
        username=username,
        full_name=f"{school.name} Ma'muri",
        email=f"{username}@edugate.uz",
        hashed_password=get_password_hash(raw_password),
        role=UserRole.SCHOOL_ADMIN,
        is_superadmin=False,
        is_active=True,
    )
    db.add(school_admin)

    await record_audit(
        db,
        user=current_user,
        action="SCHOOL_CREATE",
        target_type="SCHOOL",
        target_id=school.id,
        details=f"{school.name} ({school.code}) va login '{username}' yaratildi",
        request=request,
    )
    await db.commit()
    await db.refresh(school)

    return SchoolOut(
        id=school.id,
        name=school.name,
        code=school.code,
        address=school.address,
        phone=school.phone,
        settings=school.settings or {},
        admin_username=username,
        created_at=school.created_at,
    )


@router.get("/", response_model=List[SchoolOut], summary="Maktablar ro'yxati")
async def list_schools(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role == UserRole.SCHOOL_ADMIN:
        result = await db.execute(select(School).filter(School.id == current_user.school_id))
    else:
        result = await db.execute(select(School).order_by(School.created_at.desc()))

    schools = result.scalars().all()
    if not schools:
        return []

    school_ids = [s.id for s in schools]
    users_res = await db.execute(
        select(User.school_id, User.username).filter(
            User.school_id.in_(school_ids), User.role == UserRole.SCHOOL_ADMIN
        )
    )
    admin_map = {sid: uname for sid, uname in users_res.all()}

    return [
        SchoolOut(
            id=sc.id,
            name=sc.name,
            code=sc.code,
            address=sc.address,
            phone=sc.phone,
            settings=sc.settings or {},
            admin_username=admin_map.get(sc.id),
            created_at=sc.created_at,
        )
        for sc in schools
    ]
