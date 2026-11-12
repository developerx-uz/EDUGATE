import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import debounce_manager
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dastur ishga tushganda: Baza jadvallarini tekshirish/yaratish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Avto-migratsiya
        try:
            await conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS pinfl VARCHAR(14);"))
            await conn.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS birth_cert_number VARCHAR(50);"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'SUPERADMIN';"))
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS school_id VARCHAR(36);"))
        except Exception:
            pass

    # Initial Hokimlik Superadmin foydalanuvchisini yaratish
    async with AsyncSession(engine) as session:
        res = await session.execute(select(User).filter(User.username == "admin"))
        user = res.scalar_one_or_none()
        if not user:
            superadmin = User(
                username="admin",
                email="hokimiyat@edugate.uz",
                full_name="Viloyat va Shahar Hokimligi Superadmini",
                hashed_password=get_password_hash("Daminol007$"),
                role=UserRole.SUPERADMIN,
                is_superadmin=True,
                is_active=True
            )
            session.add(superadmin)
            await session.commit()

    # Redis keshini ishga tushirish
    await debounce_manager.initialize()
    yield
    # Dastur to'xtaganda
    await engine.dispose()


root_path = os.getenv("ROOT_PATH", "/edugate")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="EDUGATE — Maktablar uchun Face ID, Kameralar va Turniketlar bilan ishlovchi aqlli davomat tizimi yadrosi.",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path=root_path,
    lifespan=lifespan
)

# CORS (Frontend Web Admin va Mobil ilova uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static fayllar
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Marshrutlar
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/admin", response_class=HTMLResponse, tags=["Admin Panel"])
@app.get("/admin/", response_class=HTMLResponse, tags=["Admin Panel"])
async def serve_admin_panel():
    admin_html = os.path.join(os.path.dirname(__file__), "static", "admin", "index.html")
    if os.path.exists(admin_html):
        return FileResponse(admin_html)
    return HTMLResponse("<h1>EDUGATE Admin Panel topilmadi</h1>")


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "sqlite" if settings.USE_SQLITE else "postgresql"
    }
