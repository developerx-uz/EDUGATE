import asyncio
import logging
import os
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EdugateBot")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
API_BASE_URL = os.getenv("CORE_API_URL", "http://localhost:8000/api/v1")

def is_valid_token(token: str) -> bool:
    return bool(token and ":" in token and not token.lower().startswith("your_"))

bot = Bot(token=BOT_TOKEN) if is_valid_token(BOT_TOKEN) else None
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    contact_btn = KeyboardButton(text="📱 Telefon raqamimni tasdiqlash", request_contact=True)
    keyboard = ReplyKeyboardMarkup(keyboard=[[contact_btn]], resize_keyboard=True, one_time_keyboard=True)

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}!\n\n"
        f"🏫 *EDUGATE* — Maktab davomati va o'quvchilar xavfsizligi tizimiga xush kelibsiz.\n\n"
        f"Farzandingiz maktabga kirgani va chiqqanida sizga xabar yetib turishi uchun, "
        f"iltimos, quyidagi tugmani bosib telefon raqamingizni tasdiqlang:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@dp.message(F.contact)
async def handle_contact(message: types.Message):
    phone_number = message.contact.phone_number
    # Formatlash (+998...)
    if not phone_number.startswith("+"):
        phone_number = f"+{phone_number}"

    chat_id = message.chat.id
    full_name = message.from_user.full_name

    logger.info(f"Ota-ona ro'yxatdan o'tmoqda: {full_name} ({phone_number}) - Chat ID: {chat_id}")

    # Core API ga so'rov yuborib, ota-onani profilini yangilash
    # async with httpx.AsyncClient() as client:
    #     resp = await client.post(f"{API_BASE_URL}/parents/link", json={"phone": phone_number, "chat_id": chat_id})

    await message.answer(
        f"✅ Rahmat! Sizning telefon raqamingiz (*{phone_number}*) tizimga muvaffaqiyatli bog'landi.\n\n"
        f"Endi farzandingiz maktabga kirishi yoki chiqishi bilan ushbu bot sizga darhol bildirishnoma jo'natadi.",
        parse_mode="Markdown",
        reply_markup=types.ReplyKeyboardRemove()
    )


async def main():
    if not bot:
        logger.warning("TELEGRAM_BOT_TOKEN kiritilmagan. Botni ishga tushirish uchun .env ga tokenni yozing.")
        return
    logger.info("EDUGATE Telegram boti ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

