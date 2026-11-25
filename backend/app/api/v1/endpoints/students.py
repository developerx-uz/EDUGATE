from typing import List, Optional, Any
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.school import School
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.student import StudentCreate, StudentOut
from app.api.deps import get_current_user, require_not_read_only
from app.services.audit_service import record_audit
from app.services.image_utils import save_base64_image

router = APIRouter()


class GovVerifyRequest(BaseModel):
    doc_number: str
    birth_date: Optional[str] = None


class GovVerifyResponse(BaseModel):
    found: bool
    doc_number: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    pinfl: Optional[str] = None
    birth_cert_number: Optional[str] = None
    suggested_class: Optional[str] = None
    message: Optional[str] = None
    source: str = "EDUGATE Database & e-Gov API"


class PhotoUploadRequest(BaseModel):
    student_id: str
    image_base64: str


@router.post(
    "/verify-gov-id",
    response_model=GovVerifyResponse,
    summary="Hujjat seriyasi va Tug'ilgan sana bo'yicha o'quvchi ma'lumotlarini olish",
)
async def verify_government_id(
    req: GovVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    doc = req.doc_number.strip().upper().replace(" ", "")
    bdate = req.birth_date.strip() if req.birth_date else None

    if len(doc) < 3:
        raise HTTPException(
            status_code=400, detail="Hujjat seriyasi, guvohnoma yoki JSHSHIR kodi noto'g'ri."
        )

    query = (
        select(Student)
        .options(selectinload(Student.parents))
        .filter(
            or_(
                Student.pinfl == doc,
                Student.birth_cert_number == doc,
                Student.student_code == doc,
                Student.rfid_card_id == doc,
            )
        )
    )
    if current_user.role == UserRole.SCHOOL_ADMIN and current_user.school_id:
        query = query.filter(Student.school_id == current_user.school_id)

    result = await db.execute(query)
    existing_student = result.scalar_one_or_none()

    if existing_student:
        return GovVerifyResponse(
            found=True,
            doc_number=req.doc_number,
            first_name=existing_student.first_name,
            last_name=existing_student.last_name,
            pinfl=existing_student.pinfl,
            birth_cert_number=existing_student.birth_cert_number,
            suggested_class=existing_student.class_name,
            message=f"O'quvchi ma'lumotlari bazadan aniq topildi. (Sana: {bdate or 'Kiritilgan'})",
            source="EDUGATE Ma'lumotlar Bazasi (Aniq Natija)",
        )

    if settings.EMAKTAB_API_TOKEN:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    f"{settings.EMAKTAB_API_URL}/students/verify-identity",
                    json={"doc_number": doc, "birth_date": bdate},
                    headers={"Authorization": f"Bearer {settings.EMAKTAB_API_TOKEN}"},
                )
                if res.status_code == 200:
                    data = res.json()
                    if data.get("student"):
                        st_data = data["student"]
                        return GovVerifyResponse(
                            found=True,
                            doc_number=req.doc_number,
                            first_name=st_data.get("first_name"),
                            last_name=st_data.get("last_name"),
                            pinfl=st_data.get("pinfl"),
                            birth_cert_number=st_data.get("birth_cert_number"),
                            suggested_class=st_data.get("class_name"),
                            message="Ma'lumotlar e-Maktab rasmiy tizimidan muvaffaqiyatli olindi.",
                            source="MMTV e-Maktab Rasmiy API",
                        )
        except Exception:
            pass

    return GovVerifyResponse(
        found=False,
        doc_number=req.doc_number,
        message=(
            f"Ushbu hujjat ({doc}) va tug'ilgan sana ({bdate or 'kiritilmagan'}) bo'yicha "
            "ma'lumot bazada yo'q. O'quvchi ismi-familiyasini kiritishingiz mumkin."
        ),
        source="Tizim Qidiruv Natijasi",
    )


@router.post(
    "/upload-photo-base64",
    summary="O'quvchining yuz fotosuratini yuklash (Base64)",
)
async def upload_student_photo_base64(
    request: Request,
    req: PhotoUploadRequest,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(select(Student).filter(Student.id == req.student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="O'quvchi topilmadi")

    if current_user.role == UserRole.SCHOOL_ADMIN and student.school_id != current_user.school_id:
        raise HTTPException(
            status_code=403, detail="Boshqa maktab o'quvchisi rasmini yangilash taqiqlangan."
        )

    try:
        rel_path, descriptor = save_base64_image(
            req.image_base64,
            subfolder="students",
            filename_prefix=f"student_{student.id}",
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    student.photo_path = rel_path
    student.face_encoding = descriptor
    await record_audit(
        db,
        user=current_user,
        action="STUDENT_PHOTO_UPLOAD",
        target_type="STUDENT",
        target_id=student.id,
        details=f"{student.full_name} uchun Face ID rasmi yuklandi",
        request=request,
    )
    await db.commit()

    return {
        "message": "O'quvchining yuz rasmi va Face ID belgisi muvaffaqiyatli saqlandi!",
        "photo_path": rel_path,
        "has_face_encoding": True,
    }


@router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED, summary="Yangi o'quvchi qo'shish")
async def create_student(
    request: Request,
    student_in: StudentCreate,
    current_user: User = Depends(require_not_read_only),
    db: AsyncSession = Depends(get_db),
):
    effective_school_id = (
        current_user.school_id
        if current_user.role == UserRole.SCHOOL_ADMIN
        else (student_in.school_id or current_user.school_id)
    )
    if not effective_school_id:
        raise HTTPException(status_code=400, detail="Maktab tanlanishi shart")

    school_exists = (
        await db.execute(select(School.id).filter(School.id == effective_school_id))
    ).scalar_one_or_none()
    if not school_exists:
        raise HTTPException(status_code=404, detail="Tanlangan maktab topilmadi")

    code_clean = student_in.student_code.strip()
    dup = (
        await db.execute(select(Student.id).filter(Student.student_code == code_clean))
    ).scalar_one_or_none()
    if dup:
        raise HTTPException(
            status_code=400, detail=f"'{code_clean}' o'quvchi kodi allaqachon ro'yxatdan o'tgan."
        )

    photo_path = student_in.photo_path
    face_encoding = student_in.face_encoding
    if face_encoding and face_encoding.startswith("data:image/"):
        try:
            photo_path, face_encoding = save_base64_image(
                face_encoding,
                subfolder="students",
                filename_prefix=f"student_{code_clean}",
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

    student = Student(
        school_id=effective_school_id,
        first_name=student_in.first_name.strip(),
        last_name=student_in.last_name.strip(),
        student_code=code_clean,
        class_name=student_in.class_name.strip(),
        pinfl=student_in.pinfl.strip() if student_in.pinfl else None,
        birth_cert_number=student_in.birth_cert_number.strip() if student_in.birth_cert_number else None,
        gender=student_in.gender,
        rfid_card_id=student_in.rfid_card_id.strip() if student_in.rfid_card_id else None,
        face_encoding=face_encoding,
        photo_path=photo_path,
    )
    db.add(student)
    await db.flush()

    await record_audit(
        db,
        user=current_user,
        action="STUDENT_CREATE",
        target_type="STUDENT",
        target_id=student.id,
        details=f"{student.full_name} ({student.class_name}, {student.student_code}) qo'shildi",
        request=request,
    )
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/", response_model=List[StudentOut], summary="O'quvchilar ro'yxati")
async def list_students(
    school_id: Optional[str] = None,
    class_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    effective_school_id = (
        current_user.school_id
        if current_user.role == UserRole.SCHOOL_ADMIN
        else (school_id or current_user.school_id)
    )
    query = select(Student).filter(Student.is_active == True)
    if effective_school_id:
        query = query.filter(Student.school_id == effective_school_id)
    if class_name:
        query = query.filter(Student.class_name == class_name)
    result = await db.execute(query.order_by(Student.created_at.desc()))
    return result.scalars().all()
