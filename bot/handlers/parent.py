import html
import logging
from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from bot.keyboards.menu import (
    get_phone_request_kb,
    get_parent_main_menu,
    get_children_inline_kb,
)
from bot.services.api import api_client

logger = logging.getLogger("EdugateBot.Parent")
router = Router(name="parent_router")


class AbsenceForm(StatesGroup):
    waiting_for_student = State()
    waiting_for_reason = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    full_name = html.escape(message.from_user.full_name or "Hurmatli foydalanuvchi")
    await message.answer(
        f"Assalomu alaykum, <b>{full_name}</b>!\n\n"
        f"🏫 <b>EDUGATE</b> — Maktablarda Face ID va Aqlli Turniketlar orqali davomat va o'quvchilar xavfsizligini ta'minlash tizimining rasmiy botiga xush kelibsiz.\n\n"
        f"📌 <i>Farzandingiz maktabga kirgani yoki chiqqanida aniq vaqti bilan xabarnoma olish uchun telefon raqamingizni tasdiqlang:</i>",
        parse_mode="HTML",
        reply_markup=get_phone_request_kb(),
    )


@router.message(F.contact)
async def handle_phone_contact(message: types.Message):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"
    chat_id = message.chat.id
    name = message.from_user.full_name or "Ota-ona"
    username = message.from_user.username

    res = await api_client.link_parent(phone, chat_id, name, username)
    if res.get("success"):
        children_count = res.get("children_count", 0)
        extra = (
            f"\n👨‍👩‍👧 Sizga <b>{children_count} nafar</b> o'quvchi biriktirilgan."
            if children_count > 0
            else "\nℹ️ <i>Maktab ma'muriyati farzandingizni telefon raqamingizga biriktirgach, barcha ma'lumotlar avtomatik ko'rinadi.</i>"
        )
        await message.answer(
            f"✅ <b>Tabriklaymiz!</b> Telefon raqamingiz (<code>{html.escape(phone)}</code>) EDUGATE tizimiga muvaffaqiyatli bog'landi.{extra}",
            parse_mode="HTML",
            reply_markup=get_parent_main_menu(),
        )
    else:
        await message.answer(
            "⚠️ Hozircha markaziy server bilan bog'lanib bo'lmadi. Iltimos, birozdan so'ng qayta urinib ko'ring.",
            parse_mode="HTML",
            reply_markup=get_parent_main_menu(),
        )


@router.message(F.text == "📊 Bugungi Davomat")
async def show_today_attendance(message: types.Message):
    children = await api_client.get_children(message.chat.id)
    if not children:
        await message.answer(
            "ℹ️ Sizning hisobingizga hali farzand biriktirilmagan.\n\n"
            "• Avval telefon raqamingizni yuboring (/start).\n"
            "• So'ngra maktab ma'muriyatidan raqamingizni o'quvchiga biriktirishni so'rang.",
            parse_mode="HTML",
        )
        return

    text = "📊 <b>Bugungi Davomat Ko'rsatkichlari:</b>\n\n"
    for c in children:
        c_name = html.escape(c.get("full_name") or f"{c.get('first_name', '')} {c.get('last_name', '')}")
        cls_name = html.escape(c.get("class_name") or "-")
        school_name = html.escape(c.get("school_name") or "-")
        status_str = html.escape(c.get("today_status") or "Ma'lumot yo'q")
        entry_time = html.escape(c.get("entry_time") or "-")
        exit_time = html.escape(c.get("exit_time") or "Hali maktabda")
        device_name = html.escape(c.get("device_name") or "Turniket")

        text += (
            f"👤 <b>{c_name}</b> ({cls_name})\n"
            f"🏫 <b>Maktab:</b> {school_name}\n"
            f"📌 <b>Holat:</b> {status_str}\n"
            f"🟢 <b>Kirish:</b> {entry_time} ({device_name})\n"
            f"🔴 <b>Chiqish:</b> {exit_time}\n\n"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🗓 Oylik Hisobot")
async def show_monthly_report(message: types.Message):
    report = await api_client.get_monthly_report(message.chat.id)
    if not report or not report.get("linked") or not report.get("children"):
        await message.answer(
            "ℹ️ Oylik hisobotni ko'rish uchun avval hisobingizga farzand biriktirilishi zarur.",
            parse_mode="HTML",
        )
        return

    month_label = html.escape(report.get("month_label") or "")
    lines = [f"📅 <b>Joriy Oy Davomati ({month_label}):</b>\n"]
    for ch in report["children"]:
        lines.append(
            f"👤 <b>{html.escape(ch['student_name'])}</b> ({html.escape(ch['class_name'])})\n"
            f"• O'qish kunlari: <b>{ch['study_days']}</b>\n"
            f"• Qatnashgan: <b>{ch['present_days']} kun ({ch['attendance_rate']}%)</b>\n"
            f"• O'z vaqtida: <b>{ch['on_time_days']} kun</b>\n"
            f"• Kechikkan: <b>{ch['late_days']} kun</b>\n"
            f"• Qoldirgan: <b>{ch['missed_days']} kun</b>\n"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.text == "📝 Sababli Dars Qoldirish (Ariza)")
async def start_absence_flow(message: types.Message, state: FSMContext):
    children = await api_client.get_children(message.chat.id)
    if not children:
        await message.answer(
            "ℹ️ Ariza yuborish uchun avval tizimga farzandingiz biriktirilgan bo'lishi kerak (/start).",
            parse_mode="HTML",
        )
        return

    if len(children) == 1:
        await state.update_data(student_id=children[0]["id"], student_name=children[0]["full_name"])
        await state.set_state(AbsenceForm.waiting_for_reason)
        await message.answer(
            f"📝 <b>Sababli Dars Qoldirish Arizasi</b> ({html.escape(children[0]['full_name'])})\n\n"
            f"Iltimos, darsga kelolmaslik sababini qisqacha yozib yuboring.\n"
            f"<i>Bekor qilish uchun /cancel deb yozing.</i>",
            parse_mode="HTML",
        )
        return

    await state.set_state(AbsenceForm.waiting_for_student)
    await message.answer(
        "👨‍👩‍👧 Qaysi farzandingiz uchun sababli ariza yubormoqchisiz?",
        reply_markup=get_children_inline_kb(children),
    )


@router.callback_query(AbsenceForm.waiting_for_student, F.data.startswith("child_"))
async def pick_absence_student(call: types.CallbackQuery, state: FSMContext):
    student_id = call.data.split("child_", 1)[1]
    await state.update_data(student_id=student_id)
    await state.set_state(AbsenceForm.waiting_for_reason)
    await call.message.answer(
        "📝 Endi darsga kelolmaslik sababini yozib yuboring (bekor qilish: /cancel):"
    )
    await call.answer()


@router.message(AbsenceForm.waiting_for_reason)
async def handle_absence_reason(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, sababni matn ko'rinishida yozib yuboring (bekor qilish: /cancel).")
        return

    if message.text.strip().lower() == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_parent_main_menu())
        return

    data = await state.get_data()
    student_id = data.get("student_id")
    reason_text = message.text.strip()
    today_str = datetime.now().strftime("%Y-%m-%d")

    ok = await api_client.submit_absence_reason(
        student_id=student_id,
        reason=reason_text,
        date_str=today_str,
        parent_chat_id=message.chat.id,
    )
    await state.clear()

    if ok:
        await message.answer(
            "✅ <b>Arizangiz qabul qilindi!</b>\n\n"
            "Xabaringiz maktab ma'muriyati va sinf rahbari kabinetiga yuborildi.",
            parse_mode="HTML",
            reply_markup=get_parent_main_menu(),
        )
    else:
        await message.answer(
            "⚠️ Arizani saqlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
            parse_mode="HTML",
            reply_markup=get_parent_main_menu(),
        )


@router.message(F.text == "👨‍👩‍👧 Farzandlarim")
async def show_my_children(message: types.Message):
    children = await api_client.get_children(message.chat.id)
    if not children:
        await message.answer(
            "👨‍👩‍👧 Sizga biriktirilgan o'quvchilar topilmadi.\n"
            "Maktabingiz ma'muriyatiga telefon raqamingizni taqdim eting.",
            parse_mode="HTML",
        )
        return

    lines = ["👨‍👩‍👧 <b>Sizga biriktirilgan o'quvchilar:</b>\n"]
    for idx, c in enumerate(children, 1):
        face_status = "🟢 Faol (Face ID bazada)" if c.get("has_face_id") else "🟡 Kutilmoqda"
        lines.append(
            f"{idx}. <b>{html.escape(c.get('full_name', '-'))}</b> — {html.escape(c.get('class_name', '-'))} ({html.escape(c.get('school_name', '-'))})\n"
            f"• ID kod: <code>{html.escape(c.get('student_code', '-'))}</code>\n"
            f"• PINFL: <code>{html.escape(c.get('pinfl') or '-')}</code>\n"
            f"• Biometriya: {face_status}\n"
        )
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.text == "🏫 Maktab Ma'muriyati")
async def show_school_contacts(message: types.Message):
    info = await api_client.get_school_info(message.chat.id)
    if not info or not info.get("linked") or not info.get("schools"):
        await message.answer(
            "🏫 Maktab ma'lumotlari hozircha biriktirilmagan. Bog'lanish uchun +998 71 200 00 20 ga qo'ng'iroq qilishingiz mumkin.",
            parse_mode="HTML",
        )
        return

    blocks = []
    for s in info["schools"]:
        teacher_line = (
            f"• <b>Sinf rahbari ({html.escape(s.get('class_name') or '')}):</b> "
            f"{html.escape(s['class_teacher'])} ({html.escape(s.get('class_teacher_phone') or '-')})\n"
            if s.get("class_teacher")
            else ""
        )
        blocks.append(
            f"🏫 <b>{html.escape(s['school_name'])}</b> ({html.escape(s['school_code'])})\n"
            f"• <b>Telefon:</b> {html.escape(s.get('phone') or 'Kiritilmagan')}\n"
            f"• <b>Manzil:</b> {html.escape(s.get('address') or 'Kiritilmagan')}\n"
            f"{teacher_line}"
        )
    await message.answer("\n".join(blocks), parse_mode="HTML")


@router.message(F.text == "⚙️ Sozlamalar & Yordam")
async def show_help(message: types.Message):
    await message.answer(
        "⚙️ <b>EDUGATE Yordam Markazi</b>\n\n"
        "• Telefon raqamni qayta ulash: /start\n"
        "• Sababli ariza yuborish: 📝 menyudan foydalaning\n"
        "• Texnik yordam (24/7): <b>+998 71 200 00 20</b>\n"
        "• Veb-portal: https://developerx.uz/edugate/",
        parse_mode="HTML",
    )
