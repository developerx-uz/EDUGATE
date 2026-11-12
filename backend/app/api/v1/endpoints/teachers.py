from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherOut

router = APIRouter()


@router.post("/", response_model=TeacherOut, status_code=status.HTTP_201_CREATED, summary="Yangi o'qituvchi qo'shish")
async def create_teacher(
    teacher_in: TeacherCreate,
    db: AsyncSession = Depends(get_db)
):
    teacher = Teacher(
        school_id=teacher_in.school_id,
        first_name=teacher_in.first_name,
        last_name=teacher_in.last_name,
        phone_number=teacher_in.phone_number,
        subject=teacher_in.subject,
        class_name=teacher_in.class_name
    )
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


@router.get("/", response_model=List[TeacherOut], summary="O'qituvchilar ro'yxati")
async def list_teachers(
    school_id: str,
    class_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(Teacher).filter(Teacher.school_id == school_id, Teacher.is_active == True)
    if class_name:
        query = query.filter(Teacher.class_name == class_name)
    result = await db.execute(query.order_by(Teacher.created_at.desc()))
    return result.scalars().all()


@router.delete("/{teacher_id}", summary="O'qituvchini o'chirish")
async def delete_teacher(
    teacher_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(Teacher).filter(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")

    await db.delete(teacher)
    await db.commit()
    return {"message": "O'qituvchi muvaffaqiyatli o'chirildi"}
