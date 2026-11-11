from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.school import School
from app.schemas.school import SchoolCreate, SchoolOut

router = APIRouter()


@router.post("/", response_model=SchoolOut, status_code=status.HTTP_201_CREATED, summary="Yangi maktab yaratish")
async def create_school(
    school_in: SchoolCreate,
    db: AsyncSession = Depends(get_db)
):
    school = School(
        name=school_in.name,
        code=school_in.code,
        address=school_in.address,
        phone=school_in.phone,
        settings=school_in.settings or {}
    )
    db.add(school)
    await db.commit()
    await db.refresh(school)
    return school


@router.get("/", response_model=List[SchoolOut], summary="Maktablar ro'yxati")
async def list_schools(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(School))
    return result.scalars().all()

