from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from bot.config import settings
from bot.keyboards.menu import get_order_inline_kb

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
        parse_mode="HTML"
    )
    await call.answer()

@router.message(OrderForm.waiting_for_school)
async def process_school(message: types.Message, state: FSMContext):
    await state.update_data(school=message.text)
    await state.set_state(OrderForm.waiting_for_students)
    await message.answer(
        "👥 <b>Maktabdagi jami o'quvchilar soni nechta?</b>\n"
        "(Masalan: <i>1200</i>)",
        parse_mode="HTML"
    )

@router.message(OrderForm.waiting_for_students)
async def process_students(message: types.Message, state: FSMContext):
    try:
        count = int(message.text)
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
        parse_mode="HTML"
    )

@router.message(OrderForm.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = message.text
    await state.clear()

    # Admin xabarnomasi
    admin_text = (
        f"🔔 <b>YANGI BUYURTMA — EDUGATE BOT</b>\n\n"
        f"🏫 <b>Muassasa:</b> {data.get('school')}\n"
        f"👥 <b>O'quvchilar:</b> {data.get('students')} nafar\n"
        f"🚪 <b>Turniketlar:</b> {data.get('turnstiles')} ta\n"
        f"📞 <b>Aloqa:</b> {phone}\n"
        f"👤 <b>Yuboruvchi:</b> @{message.from_user.username or 'mavjud_emas'} ({message.from_user.full_name})"
    )

    await message.answer(
        "🎉 <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        "Mutaxassislarimiz 15 daqiqa ichida siz bilan bog'lanadi va maktabingiz uchun to'liq texnik loyiha hamda smeta taqdim etadi.",
        parse_mode="HTML"
    )

    if settings.ADMIN_CHAT_ID:
        try:
            await message.bot.send_message(settings.ADMIN_CHAT_ID, admin_text, parse_mode="HTML")
        except Exception:
            pass

