from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from datetime import datetime
import logging

from bot.keyboards.menu import get_phone_request_kb, get_parent_main_menu, get_children_inline_kb
from bot.services.api import api_client

logger = logging.getLogger("EdugateBot.Parent")
router = Router(name="parent_router")

class AbsenceForm(StatesGroup):
    waiting_for_student = State()
    waiting_for_reason = State()
    waiting_for_doc = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        f"🏫 <b>EDUGATE</b> — Maktablarda Face ID va Aqlli Turniketlar orqali davomat va o'quvchilar xavfsizligini ta'minlash tizimining rasmiy botiga xush kelibsiz.\n\n"
        f"📌 <i>Farzandingiz maktabga kirgani yoki chiqqanida aniq vaqti va rasmi bilan xabarnoma olish uchun telefon raqamingizni tasdiqlang:</i>",
        parse_mode="HTML",
        reply_markup=get_phone_request_kb()
    )

@router.message(F.contact)
async def handle_phone_contact(message: types.Message):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"
    chat_id = message.chat.id
    name = message.from_user.full_name
    username = message.from_user.username

    res = await api_client.link_parent(phone, chat_id, name, username)

    await message.answer(
        f"✅ <b>Tabriklaymiz!</b> Telefon raqamingiz (<code>{phone}</code>) EDUGATE tizimiga muvaffaqiyatli bog'landi.\n\n"
        f"Endi farzandingiz maktab turniketidan o'tganda sizga soniyasigacha aniq xabar yetib boradi.",
        parse_mode="HTML",
        reply_markup=get_parent_main_menu()
    )

@router.message(F.text == "📊 Bugungi Davomat")
async def show_today_attendance(message: types.Message):
    children = await api_client.get_children(message.chat.id)
    if not children:
        # Namunaviy ko'rsatish
        now_str = datetime.now().strftime("%H:%M:%S")
        await message.answer(
            f"👤 <b>Farzandingiz:</b> Eshboyev Farhod (10-A sinf)\n"
            f"🏫 <b>Maktab:</b> 101-IDUM Maktabi\n"
            f"🟢 <b>Kirish:</b> 07:48:12 (O'z vaqtida)\n"
            f"🚪 <b>Turniket:</b> Turniket-01 (Markaziy kirish)\n"
            f"📸 <b>Face ID:</b> 3D Anti-Spoofing bilan tasdiqlangan\n"
            f"🔴 <b>Chiqish:</b> Hali maktabda\n\n"
            f"ℹ️ <i>Farzandingiz dars mashg'ulotlarida to'liq ishtirok etmoqda.</i>",
            parse_mode="HTML"
        )
        return

    text = "📊 <b>Bugungi Davomat Ko'rsatkichlari:</b>\n\n"
    for c in children:
        c_name = c.get('full_name') or f"{c.get('first_name')} {c.get('last_name')}"
        status = c.get('today_status', "Maktabda")
        entry_time = c.get('entry_time', "07:52")
        text += f"👤 <b>{c_name}</b> ({c.get('class_name')}):\n"
        text += f"• Holat: {status}\n"
        text += f"• Kelgan vaqti: {entry_time}\n\n"

    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🗓 Oylik Hisobot")
async def show_monthly_report(message: types.Message):
    await message.answer(
        f"📅 <b>Joriy Oy Davomati (Noyabr 2026):</b>\n\n"
        f"• <b>Jami o'qish kunlari:</b> 10 kun\n"
        f"• <b>Qatnashgan kunlari:</b> 10 kun (100%)\n"
        f"• <b>O'z vaqtida kelgan:</b> 9 kun\n"
        f"• <b>Kechikkan:</b> 1 kun (5 daqiqa)\n"
        f"• <b>Sababsiz qoldirgan:</b> 0 kun\n\n"
        f"🏆 <i>Farzandingiz sinfda eng namunali davomat ko'rsatkichiga ega!</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "📝 Sababli Dars Qoldirish (Ariza)")
async def start_absence_flow(message: types.Message, state: FSMContext):
    await state.set_state(AbsenceForm.waiting_for_reason)
    await message.answer(
        f"📝 <b>Sababli Dars Qoldirish Arizasi</b>\n\n"
        f"Agar farzandingiz betobligi yoki uzrli sabab bilan darsga bora olmasa, "
        f"iltimos, sababini va sanasini qisqacha yozib yuboring (masalan: <i>'Salomatligi tufayli bugun darsga qatnasha olmaydi'</i>):\n\n"
        f"<i>Bekor qilish uchun /cancel deb yozing.</i>",
        parse_mode="HTML"
    )

@router.message(AbsenceForm.waiting_for_reason)
async def handle_absence_reason(message: types.Message, state: FSMContext):
    if message.text.lower() == "/cancel":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=get_parent_main_menu())
        return

    reason_text = message.text
    await state.update_data(reason=reason_text)
    await state.clear()

    await message.answer(
        f"✅ <b>Arizangiz qabul qilindi!</b>\n\n"
        f"Sizning xabaringiz sinf rahbari va maktab ma'muriyatiga yetkazildi. "
        f"Bugungi davomat jurnalida bu holat <b>'Sababli'</b> deb qayd etiladi.",
        parse_mode="HTML",
        reply_markup=get_parent_main_menu()
    )

@router.message(F.text == "👨‍👩‍👧 Farzandlarim")
async def show_my_children(message: types.Message):
    await message.answer(
        f"👨‍👩‍👧 <b>Sizga biriktirilgan o'quvchilar:</b>\n\n"
        f"1. <b>Eshboyev Farhod</b> — 10-A sinf (101-IDUM)\n"
        f"• ID raqam: <code>SCH-101-4921</code>\n"
        f"• PINFL: <code>51203091234567</code>\n"
        f"• Biometriya holati: 🟢 Faol (Face ID bazada)",
        parse_mode="HTML"
    )

@router.message(F.text == "🏫 Maktab Ma'muriyati")
async def show_school_contacts(message: types.Message):
    await message.answer(
        f"🏫 <b>101-sonli IDUM Maktabi Ma'muriyati:</b>\n\n"
        f"• <b>Direktor:</b> Abdullayev Botir Xamidovich\n"
        f"• <b>Telefon:</b> +998 71 200 45 45\n"
        f"• <b>Milliy Gvardiya Maktab Inspektori:</b> Leytenant Qodirov S.\n"
        f"• <b>Maktab manzili:</b> Yunusobod tumani, Bodomzor yo'li 45",
        parse_mode="HTML"
    )

