from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentOut

router = APIRouter()


@router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED, summary="Yangi o'quvchi qo'shish")
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_db)
):
    student = Student(
        school_id=student_in.school_id,
        first_name=student_in.first_name,
        last_name=student_in.last_name,
        student_code=student_in.student_code,
        class_name=student_in.class_name,
        rfid_card_id=student_in.rfid_card_id,
        face_encoding=student_in.face_encoding
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/", response_model=List[StudentOut], summary="O'quvchilar ro'yxati")
async def list_students(
    school_id: str,
    class_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Student).filter(Student.school_id == school_id, Student.is_active == True)
    if class_name:
        query = query.filter(Student.class_name == class_name)
    result = await db.execute(query)
    return result.scalars().all()

