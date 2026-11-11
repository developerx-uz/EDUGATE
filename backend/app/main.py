from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import debounce_manager
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dastur ishga tushganda: Baza jadvallarini tekshirish/yaratish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Redis keshini ishga tushirish
    await debounce_manager.initialize()
    yield
    # Dastur to'xtaganda
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="EDUGATE — Maktablar uchun Face ID, Kameralar va Turniketlar bilan ishlovchi aqlli davomat tizimi yadrosi.",
    docs_url="/docs",
    redoc_url="/redoc",
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

# Marshrutlar
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "sqlite" if settings.USE_SQLITE else "postgresql"
    }
