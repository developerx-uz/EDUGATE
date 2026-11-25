import html
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.config import settings
from bot.services.api import api_client

router = Router(name="order_router")


class OrderForm(StatesGroup):
    waiting_for_school = State()
    waiting_for_students = State()
    waiting_for_phone = State()


@router.callback_query(F.data == "order_equipment")
async def start_order(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(OrderForm.waiting_for_school)
    await call.message.answer(
        "🏫 <b>EDUGATE Uskunalariga Buyurtma Berish</b>\n\n"
        "Iltimos, maktabingiz yoki tashkilotingiz nomini yozing (masalan: <i>101-maktab Toshkent shahar</i>):",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(OrderForm.waiting_for_school)
async def process_school(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, maktab nomini matn ko'rinishida kiriting.")
        return
    await state.update_data(school=message.text.strip())
    await state.set_state(OrderForm.waiting_for_students)
    await message.answer(
        "👥 <b>Maktabdagi jami o'quvchilar soni nechta?</b>\n(Masalan: <i>1200</i>)",
        parse_mode="HTML",
    )


@router.message(OrderForm.waiting_for_students)
async def process_students(message: types.Message, state: FSMContext):
    try:
        count = max(1, int((message.text or "").strip()))
    except ValueError:
        count = 1000

    turnstiles = 2 if count <= 800 else (4 if count <= 1500 else 6)
    await state.update_data(students=count, turnstiles=turnstiles)
    await state.set_state(OrderForm.waiting_for_phone)
    await message.answer(
        f"✅ <b>Tavsiya etilgan hisob-kitob:</b>\n"
        f"• Turniket yo'lakchalari: <b>{turnstiles} ta</b>\n"
        f"• Face ID terminallari: <b>{turnstiles * 2} dona (Kirish + Chiqish)</b>\n"
        f"• SmartUPS zaxira quvvat: <b>1 komplekt (8 soat)</b>\n\n"
        f"Iltimos, siz bilan bog'lanishimiz uchun <b>telefon raqamingizni</b> yozing:",
        parse_mode="HTML",
    )


@router.message(OrderForm.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Iltimos, telefon raqamingizni yozib yuboring.")
        return

    data = await state.get_data()
    phone = message.text.strip()
    await state.clear()

    saved = await api_client.submit_school_order({
        "full_name": message.from_user.full_name or "Telegram Foydalanuvchi",
        "phone": phone,
        "school_name": data.get("school"),
        "students_count": data.get("students"),
        "source": "telegram_bot",
    })

    admin_text = (
        f"🔔 <b>YANGI BUYURTMA — EDUGATE BOT</b>\n\n"
        f"🏫 <b>Muassasa:</b> {html.escape(str(data.get('school', '-')))}\n"
        f"👥 <b>O'quvchilar:</b> {data.get('students')} nafar\n"
        f"🚪 <b>Turniketlar:</b> {data.get('turnstiles')} ta\n"
        f"📞 <b>Aloqa:</b> {html.escape(phone)}\n"
        f"👤 <b>Yuboruvchi:</b> @{html.escape(message.from_user.username or 'mavjud_emas')} ({html.escape(message.from_user.full_name or '')})"
    )

    await message.answer(
        "🎉 <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        "Mutaxassislarimiz tez orada siz bilan bog'lanadi va maktabingiz uchun texnik loyiha hamda smeta taqdim etadi."
        + ("" if saved else "\n<i>(Buyurtma ma'muriyatga yuborildi)</i>"),
        parse_mode="HTML",
    )

    if settings.ADMIN_CHAT_ID and settings.ADMIN_CHAT_ID != "123456789":
        try:
            await message.bot.send_message(settings.ADMIN_CHAT_ID, admin_text, parse_mode="HTML")
        except Exception:
            pass
