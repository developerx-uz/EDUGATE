import html
from typing import List, Optional, Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, require_superadmin
from app.models.lead import LeadOrder
from app.models.user import User, UserRole
from app.schemas.parent_order import LeadOrderCreate, LeadOrderOut, LeadOrderStatusUpdate
from app.services.audit_service import record_audit, get_role_str
from app.services.notifier import notifier
from app.services.settings_service import get_effective_settings

router = APIRouter()


def compute_recommended_hardware(students_count: Optional[int]) -> tuple[Optional[int], Optional[int]]:
    if not students_count or students_count <= 0:
        return None, None
    turnstiles = 2 if students_count <= 800 else (4 if students_count <= 1500 else 6)
    return turnstiles, turnstiles * 2


async def create_lead_order_record(
    db: AsyncSession,
    payload: LeadOrderCreate,
    background_tasks: BackgroundTasks,
) -> LeadOrder:
    full_name = (payload.full_name or payload.contact_name or "Noma'lum murojaat").strip()
    phone = (payload.phone or payload.phone_number or "").strip()
    if not phone:
        raise HTTPException(status_code=400, detail="Telefon raqami kiritilishi shart.")

    school_info = (payload.school_info or payload.school_name or "").strip() or None
    turnstiles, cameras = compute_recommended_hardware(payload.students_count)

    lead = LeadOrder(
        full_name=full_name,
        phone=phone,
        region=payload.region.strip() if payload.region else None,
        school_info=school_info,
        students_count=payload.students_count,
        recommended_turnstiles=turnstiles,
        recommended_cameras=cameras,
        message=payload.message.strip() if payload.message else None,
        source=payload.source or "landing_contact",
        status="NEW",
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    eff = await get_effective_settings(db)
    hw_note = (
        f"\n🚪 <b>Tavsiya:</b> {turnstiles} turniket / {cameras} Face ID"
        if turnstiles
        else ""
    )
    alert_text = (
        f"🔔 <b>YANGI ARIZA ({html.escape(lead.source)})</b>\n\n"
        f"👤 <b>Mas'ul:</b> {html.escape(lead.full_name)}\n"
        f"📞 <b>Telefon:</b> {html.escape(lead.phone)}\n"
        f"🏫 <b>Muassasa:</b> {html.escape(lead.school_info or '-')}\n"
        f"📍 <b>Hudud:</b> {html.escape(lead.region or '-')}"
        f"{hw_note}"
    )
    background_tasks.add_task(notifier.send_admin_alert, text=alert_text, chat_id=eff.admin_chat_id)
    return lead


@router.post("/new", response_model=LeadOrderOut, status_code=status.HTTP_201_CREATED, summary="Yangi turniket/kamera buyurtmasi yoki konsultatsiya arizasi")
async def create_order(
    payload: LeadOrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    return await create_lead_order_record(db, payload, background_tasks)


@router.get("/", response_model=List[LeadOrderOut], summary="Tushgan arizalar va buyurtmalar ro'yxati")
async def list_orders(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if get_role_str(current_user) == UserRole.SCHOOL_ADMIN.value:
        raise HTTPException(status_code=403, detail="Buyurtmalar faqat markaziy monitoring va superadmin uchun.")
    query = select(LeadOrder).order_by(LeadOrder.created_at.desc())
    if status_filter:
        query = query.filter(LeadOrder.status == status_filter.strip().upper())
    return (await db.execute(query.limit(100))).scalars().all()


@router.patch("/{order_id}", response_model=LeadOrderOut, summary="Ariza holatini yangilash (Faqat Superadmin)")
async def update_order_status(
    order_id: str,
    request: Request,
    payload: LeadOrderStatusUpdate,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    lead = (await db.execute(select(LeadOrder).filter(LeadOrder.id == order_id))).scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Ariza topilmadi")
    lead.status = payload.status
    await record_audit(
        db,
        user=current_user,
        action="ORDER_STATUS_UPDATE",
        target_type="LEAD_ORDER",
        target_id=lead.id,
        details=f"Ariza holati: {payload.status}",
        request=request,
    )
    await db.commit()
    await db.refresh(lead)
    return lead
