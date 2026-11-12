import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.config import settings
from bot.handlers.parent import router as parent_router
from bot.handlers.admin import router as admin_router
from bot.handlers.order import router as order_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EdugateBot")

async def main():
    if not settings.is_valid_token:
        logger.warning(
            "TELEGRAM_BOT_TOKEN kiritilmagan yoki noto'g'ri. "
            "Botni ishga tushirish uchun .env fayliga haqiqiy tokenni yozing."
        )
        return

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Routers ro'yxatdan o'tkazish
    dp.include_router(parent_router)
    dp.include_router(admin_router)
    dp.include_router(order_router)

    logger.info("EDUGATE AI & Aqlli Davomat Telegram Boti muvaffaqiyatli ishga tushdi...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
