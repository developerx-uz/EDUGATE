from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from app.schemas.teacher import TeacherCreate, TeacherOut
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=TeacherOut, status_code=status.HTTP_201_CREATED, summary="Yangi o'qituvchi qo'shish")
async def create_teacher(
    teacher_in: TeacherCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role == UserRole.MINISTRY_VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Xalq Ta'limi portali faqat monitoring (ko'rish) uchun. O'qituvchi qo'shish taqiqlangan."
        )

    effective_school_id = current_user.school_id if current_user.role == UserRole.SCHOOL_ADMIN else (teacher_in.school_id or current_user.school_id)
    if not effective_school_id:
        raise HTTPException(status_code=400, detail="Maktab tanlanishi shart")

    teacher = Teacher(
        school_id=effective_school_id,
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
    school_id: Optional[str] = None,
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    effective_school_id = current_user.school_id if current_user.role == UserRole.SCHOOL_ADMIN else (school_id or current_user.school_id)
    query = select(Teacher).filter(Teacher.is_active == True)
    if effective_school_id:
        query = query.filter(Teacher.school_id == effective_school_id)
    if class_name:
        query = query.filter(Teacher.class_name == class_name)
    result = await db.execute(query.order_by(Teacher.created_at.desc()))
    return result.scalars().all()


@router.delete("/{teacher_id}", summary="O'qituvchini o'chirish")
async def delete_teacher(
    teacher_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    if current_user.role == UserRole.MINISTRY_VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Xalq Ta'limi portali faqat monitoring (ko'rish) uchun. O'qituvchini o'chirish taqiqlangan."
        )

    result = await db.execute(select(Teacher).filter(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")

    if current_user.role == UserRole.SCHOOL_ADMIN and teacher.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab o'qituvchisini o'chirish taqiqlangan.")

    await db.delete(teacher)
    await db.commit()
    return {"message": "O'qituvchi muvaffaqiyatli o'chirildi"}
