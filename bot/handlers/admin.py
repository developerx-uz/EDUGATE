from aiogram import Router, types, F
from aiogram.filters import Command
from bot.keyboards.menu import get_admin_main_menu

router = Router(name="admin_router")

@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    await message.answer(
        "👮‍♂️ <b>EDUGATE — Maktab Ma'muriyati va Milliy Gvardiya Xavfsizlik Paneli</b>\n\n"
        "Quyidagi buyruqlar orqali maktab xavfsizligi va o'quvchilar intizomini jonli nazorat qilishingiz mumkin:",
        parse_mode="HTML",
        reply_markup=get_admin_main_menu()
    )

@router.message(F.text == "🚨 Jonli Maktab Monitoringi")
async def live_monitoring(message: types.Message):
    await message.answer(
        "🚨 <b>JONLI MAKTAB MONITORINGI (Bugun):</b>\n\n"
        "🏫 <b>101-IDUM Maktabi</b>\n"
        "• Jami o'quvchilar: <b>1,420 nafar</b>\n"
        "• Hozirda maktabda: <b>1,392 nafar (98.0%)</b>\n"
        "• O'z vaqtida kelganlar: <b>1,310</b>\n"
        "• Kechikib kelganlar: <b>82</b>\n"
        "• Kelmaganlar: <b>28 (12 sababli, 16 aniqlanmoqda)</b>\n\n"
        "🚪 <b>Turniketlar holati:</b> Barcha 4 ta yo'lak onlayn (Aloqa 100%)",
        parse_mode="HTML"
    )

@router.message(F.text == "⚠️ Kechikkanlar Ro'yxati")
async def late_students(message: types.Message):
    await message.answer(
        "⚠️ <b>Bugun kechikkan o'quvchilar (Top-5):</b>\n\n"
        "1. Karimova Nozima (8-B) — 08:14 (+14 daqiqa)\n"
        "2. To'rayev Sanjar (11-A) — 08:18 (+18 daqiqa)\n"
        "3. Yusupov Jamshid (9-V) — 08:22 (+22 daqiqa)\n"
        "4. Alimov Rustam (7-A) — 08:25 (+25 daqiqa)\n"
        "5. Zokirova Diyora (10-B) — 08:31 (+31 daqiqa)\n\n"
        "ℹ️ <i>Barcha ota-onalariga Telegram orqali kechikish xabarnomasi yuborildi.</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "🛑 Begona Shaxslar Urinishi")
async def unauthorized_access(message: types.Message):
    await message.answer(
        "🛑 <b>XAVFSIZLIK HISOBOTI — BEGONA SHAXSLAR:</b>\n\n"
        "• Oxirgi 24 soat ichida maktab turniketiga kiritilmagan begona shaxslar: <b>0 ta</b>\n"
        "• Soxta rasm yoki telefon orqali o'tishga urinish (Anti-Spoofing blokirovkasi): <b>0 ta</b>\n\n"
        "🛡 <i>Maktab perimetri to'liq nazorat ostida va begona shaxslarning kirishi 100% cheklangan.</i>",
        parse_mode="HTML"
    )

@router.message(F.text == "📞 Tezkor Favqulodda Qo'ng'iroq")
async def emergency_call(message: types.Message):
    await message.answer(
        "🚨 <b>FAVQULODDA TEZKOR ALOQA:</b>\n\n"
        "• <b>Ichki Ishlar (IIB Navbatchi):</b> 102\n"
        "• <b>Milliy Gvardiya Tezkor Guruh:</b> +998 71 234 56 78\n"
        "• <b>Yong'in Xavfsizligi (Favqulodda Vaziyatlar):</b> 101\n"
        "• <b>Tez Tibbiy Yordam:</b> 103\n"
        "• <b>EDUGATE Texnik Xizmat (24/7):</b> +998 71 200 00 20",
        parse_mode="HTML"
    )

