import html
from aiogram import Router, types, F
from aiogram.filters import Command
from bot.config import settings
from bot.keyboards.menu import get_admin_main_menu

router = Router(name="admin_router")


def _is_authorized_admin(message: types.Message) -> bool:
    configured = (settings.ADMIN_CHAT_ID or "").strip()
    if not configured or configured == "123456789":
        return False
    return str(message.chat.id) == configured


@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not _is_authorized_admin(message):
        await message.answer(
            "🔒 Admin paneli faqat tizimda tasdiqlangan ma'mur (ADMIN_CHAT_ID) uchun ochiq.\n"
            "Veb boshqaruv panelidan foydalaning."
        )
        return

    await message.answer(
        "👮‍♂️ <b>EDUGATE — Maktab Ma'muriyati va Xavfsizlik Paneli</b>\n\n"
        "Quyidagi tugmalar orqali tezkor ma'lumot olishingiz mumkin:",
        parse_mode="HTML",
        reply_markup=get_admin_main_menu(),
    )


@router.message(F.text == "🚨 Jonli Maktab Monitoringi")
async def live_monitoring(message: types.Message):
    if not _is_authorized_admin(message):
        return
    await message.answer(
        "🚨 <b>JONLI MAKTAB MONITORINGI:</b>\n\n"
        "Jonli statistika va 1-soniyalik puls ma'lumotlari veb-portalning "
        "<code>/admin</code> va <code>/school</code> bo'limlarida mavjud.",
        parse_mode="HTML",
    )


@router.message(F.text == "⚠️ Kechikkanlar Ro'yxati")
async def late_students(message: types.Message):
    if not _is_authorized_admin(message):
        return
    await message.answer(
        "⚠️ Kechikkan o'quvchilar ro'yxati real vaqt rejimida Veb-portalning "
        "<b>Bildirishnomalar</b> va <b>Jonli Davomat</b> bo'limida aks etadi.",
        parse_mode="HTML",
    )


@router.message(F.text == "🛑 Begona Shaxslar Urinishi")
async def unauthorized_access(message: types.Message):
    if not _is_authorized_admin(message):
        return
    await message.answer(
        "🛡 <b>XAVFSIZLIK HOLATI:</b>\n"
        "Turniket va Face ID qurilmalari Anti-Passback hamda token nazorati ostida ishlamoqda.",
        parse_mode="HTML",
    )


@router.message(F.text == "📞 Tezkor Favqulodda Qo'ng'iroq")
async def emergency_call(message: types.Message):
    if not _is_authorized_admin(message):
        return
    await message.answer(
        "🚨 <b>FAVQULODDA TEZKOR ALOQA:</b>\n\n"
        "• <b>Ichki Ishlar (IIB):</b> 102\n"
        "• <b>Yong'in Xavfsizligi (FVV):</b> 101\n"
        "• <b>Tez Tibbiy Yordam:</b> 103\n"
        "• <b>EDUGATE Texnik Xizmat (24/7):</b> +998 71 200 00 20",
        parse_mode="HTML",
    )


@router.message(F.text == "📈 Tuman & Viloyat Reytingi")
async def district_rating(message: types.Message):
    if not _is_authorized_admin(message):
        return
    await message.answer(
        "📈 Tuman va viloyatlar kesimidagi jonli reyting veb-portalning "
        "<b>Dashboard → Eng top Maktablar</b> hamda <b>Statistika</b> bo'limlarida ko'rsatiladi.",
        parse_mode="HTML",
    )
