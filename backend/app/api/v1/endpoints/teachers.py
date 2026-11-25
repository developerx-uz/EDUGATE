from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.school import School
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherOut
from app.api.deps import get_current_user, require_not_read_only
from app.services.audit_service import record_audit

router = APIRouter()


def _serialize_teacher(t: Teacher, school_name: Optional[str] = None) -> dict:
    return {
        "id": t.id,
        "school_id": t.school_id,
        "school_name": school_name or (t.school.name if getattr(t, "school", None) else None),
        "first_name": t.first_name,
        "last_name": t.last_name,
        "full_name": t.full_name,
        "phone_number": t.phone_number,
        "subject": t.subject,
        "class_name": t.class_name,
        "is_active": t.is_active,
        "created_at": t.created_at,
    }


@router.post("/", response_model=TeacherOut, status_code=status.HTTP_201_CREATED, summary="Yangi o'qituvchi qo'shish")
async def create_teacher(
    request: Request,
    teacher_in: TeacherCreate,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
):
    effective_school_id = (
        current_user.school_id
        if current_user.role == UserRole.SCHOOL_ADMIN
        else (teacher_in.school_id or current_user.school_id)
    )
    if not effective_school_id:
        raise HTTPException(status_code=400, detail="Maktab tanlanishi shart")

    school = (
        await db.execute(select(School).filter(School.id == effective_school_id))
    ).scalar_one_or_none()
    if not school:
        raise HTTPException(status_code=404, detail="Tanlangan maktab topilmadi")

    teacher = Teacher(
        school_id=effective_school_id,
        first_name=teacher_in.first_name.strip(),
        last_name=teacher_in.last_name.strip(),
        phone_number=teacher_in.phone_number.strip() if teacher_in.phone_number else None,
        subject=teacher_in.subject.strip() if teacher_in.subject else None,
        class_name=teacher_in.class_name.strip() if teacher_in.class_name else None,
    )
    db.add(teacher)
    await db.flush()
    await record_audit(
        db,
        user=current_user,
        action="TEACHER_CREATE",
        target_type="TEACHER",
        target_id=teacher.id,
        details=f"{teacher.full_name} ({teacher.subject or 'O\'qituvchi'}) qo'shildi",
        request=request,
    )
    await db.commit()
    await db.refresh(teacher)
    return _serialize_teacher(teacher, school.name)


@router.get("/", response_model=List[TeacherOut], summary="O'qituvchilar ro'yxati")
async def list_teachers(
    school_id: Optional[str] = None,
    class_name: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    effective_school_id = (
        current_user.school_id
        if current_user.role == UserRole.SCHOOL_ADMIN
        else (school_id or current_user.school_id)
    )
    query = select(Teacher).options(selectinload(Teacher.school)).filter(Teacher.is_active == True)
    if effective_school_id:
        query = query.filter(Teacher.school_id == effective_school_id)
    if class_name:
        query = query.filter(Teacher.class_name == class_name)
    result = await db.execute(query.order_by(Teacher.created_at.desc()))
    teachers = result.scalars().all()
    return [_serialize_teacher(t) for t in teachers]


@router.put("/{teacher_id}", response_model=TeacherOut, summary="O'qituvchini tahrirlash")
async def update_teacher(
    teacher_id: str,
    request: Request,
    payload: TeacherUpdate,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Teacher).options(selectinload(Teacher.school)).filter(Teacher.id == teacher_id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")

    if current_user.role == UserRole.SCHOOL_ADMIN and teacher.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab o'qituvchisini tahrirlash taqiqlangan.")

    for field, val in payload.model_dump(exclude_unset=True).items():
        setattr(teacher, field, val.strip() if isinstance(val, str) else val)

    await record_audit(
        db,
        user=current_user,
        action="TEACHER_UPDATE",
        target_type="TEACHER",
        target_id=teacher.id,
        details=f"{teacher.full_name} ma'lumotlari yangilandi",
        request=request,
    )
    await db.commit()
    await db.refresh(teacher)
    return _serialize_teacher(teacher)


@router.delete("/{teacher_id}", summary="O'qituvchini o'chirish")
async def delete_teacher(
    teacher_id: str,
    request: Request,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Teacher).filter(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="O'qituvchi topilmadi")

    if current_user.role == UserRole.SCHOOL_ADMIN and teacher.school_id != current_user.school_id:
        raise HTTPException(status_code=403, detail="Boshqa maktab o'qituvchisini o'chirish taqiqlangan.")

    t_name = teacher.full_name
    await db.delete(teacher)
    await record_audit(
        db,
        user=current_user,
        action="TEACHER_DELETE",
        target_type="TEACHER",
        target_id=teacher_id,
        details=f"{t_name} o'chirildi",
        request=request,
    )
    await db.commit()
    return {"message": "O'qituvchi muvaffaqiyatli o'chirildi"}
