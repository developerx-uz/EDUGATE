from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.school import School
from app.models.user import User, UserRole
from app.schemas.school import SchoolCreate, SchoolOut
from app.api.deps import get_current_user, require_superadmin

router = APIRouter()


@router.post("/", response_model=SchoolOut, status_code=status.HTTP_201_CREATED, summary="Yangi maktab va uning yagona loginini yaratish (Faqat Superadmin)")
async def create_school(
    school_in: SchoolCreate,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    # Maktab kodi mavjudligini tekshirish
    existing_school = (await db.execute(select(School).filter(School.code == school_in.code.strip()))).scalar_one_or_none()
    if existing_school:
        raise HTTPException(status_code=400, detail=f"'{school_in.code}' kodli maktab allaqachon mavjud.")

    # Maktab yaratish
    school = School(
        name=school_in.name.strip(),
        code=school_in.code.strip(),
        address=school_in.address.strip() if school_in.address else None,
        phone=school_in.phone.strip() if school_in.phone else None,
        settings=school_in.settings or {}
    )
    db.add(school)
    await db.commit()
    await db.refresh(school)

    # Qat'iy talab: Har bir maktab uchun 1 ta login bo'lishi shart (2-mumkin emas)
    username = (school_in.admin_username or f"maktab_{school.code.lower()}").strip().lower()
    raw_password = (school_in.admin_password or f"Maktab_{school.code}2026!").strip()

    # Login band emasligini tekshirish
    existing_user = (await db.execute(select(User).filter(User.username == username))).scalar_one_or_none()
    if existing_user:
        # Agar bu login band bo'lsa, unikal nom yasaymiz
        username = f"maktab_{school.code.lower()}_{school.id[:4]}"

    school_admin = User(
        school_id=school.id,
        username=username,
        full_name=f"{school.name} Ma'muri",
        email=f"{username}@edugate.uz",
        hashed_password=get_password_hash(raw_password),
        role=UserRole.SCHOOL_ADMIN,
        is_superadmin=False,
        is_active=True
    )
    db.add(school_admin)
    await db.commit()

    return SchoolOut(
        id=school.id,
        name=school.name,
        code=school.code,
        address=school.address,
        phone=school.phone,
        settings=school.settings or {},
        admin_username=username,
        created_at=school.created_at
    )


@router.get("/", response_model=List[SchoolOut], summary="Maktablar ro'yxati")
async def list_schools(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == UserRole.SCHOOL_ADMIN:
        result = await db.execute(select(School).filter(School.id == current_user.school_id))
    else:
        result = await db.execute(select(School).order_by(School.created_at.desc()))
    
    schools = result.scalars().all()
    output = []
    for sc in schools:
        # Bog'langan 1 ta loginni topish
        res_u = await db.execute(select(User.username).filter(User.school_id == sc.id, User.role == UserRole.SCHOOL_ADMIN))
        uname = res_u.scalar_one_or_none()
        output.append(SchoolOut(
            id=sc.id,
            name=sc.name,
            code=sc.code,
            address=sc.address,
            phone=sc.phone,
            settings=sc.settings or {},
            admin_username=uname,
            created_at=sc.created_at
        ))
    return output

