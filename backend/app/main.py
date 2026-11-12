import os
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
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

landing_dir = os.path.join(os.path.dirname(__file__), "static", "landing")
landing_assets_dir = os.path.join(landing_dir, "assets")

admin_dir_path = os.path.join(os.path.dirname(__file__), "static", "admin")
if os.path.exists(admin_dir_path):
    css_dir = os.path.join(admin_dir_path, "css")
    js_dir = os.path.join(admin_dir_path, "js")
    if os.path.exists(css_dir):
        app.mount("/admin/css", StaticFiles(directory=css_dir), name="admin-css")
    if os.path.exists(js_dir):
        app.mount("/admin/js", StaticFiles(directory=js_dir), name="admin-js")


# Marshrutlar
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", response_class=HTMLResponse, tags=["Public Portal"])
@app.get("/index.html", response_class=HTMLResponse, tags=["Public Portal"])
async def serve_landing():
    landing_index = os.path.join(os.path.dirname(__file__), "static", "landing", "index.html")
    if os.path.exists(landing_index):
        with open(landing_index, "r", encoding="utf-8") as f:
            content = f.read()
        response = HTMLResponse(content=content)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return HTMLResponse("<h1>EDUGATE — Davomat va Xavfsizlik Ekotizimi</h1>")


@app.get("/Orlan-logo.png", tags=["Public Portal"])
async def serve_landing_logo():
    logo_file = os.path.join(os.path.dirname(__file__), "static", "landing", "Orlan-logo.png")
    if os.path.exists(logo_file):
        return FileResponse(logo_file, media_type="image/png")
    return HTMLResponse(status_code=404)


@app.get("/assets/{file_path:path}", tags=["Public Portal"])
@app.get("/edugate/assets/{file_path:path}", tags=["Public Portal"])
async def serve_landing_asset(file_path: str):
    landing_assets = os.path.join(os.path.dirname(__file__), "static", "landing", "assets")
    full_path = os.path.join(landing_assets, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        media_type = None
        if full_path.endswith('.css'):
            media_type = 'text/css; charset=utf-8'
        elif full_path.endswith('.js'):
            media_type = 'application/javascript; charset=utf-8'
        return FileResponse(full_path, media_type=media_type)
    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/css/{file_path:path}", tags=["Static"])
@app.get("/edugate/css/{file_path:path}", tags=["Static"])
async def serve_css(file_path: str):
    landing_css = os.path.join(os.path.dirname(__file__), "static", "landing", "css", file_path)
    admin_css = os.path.join(os.path.dirname(__file__), "static", "admin", "css", file_path)
    if os.path.exists(landing_css) and os.path.isfile(landing_css):
        return FileResponse(landing_css, media_type="text/css; charset=utf-8")
    if os.path.exists(admin_css) and os.path.isfile(admin_css):
        return FileResponse(admin_css, media_type="text/css; charset=utf-8")
    raise HTTPException(status_code=404, detail="CSS not found")


@app.get("/js/{file_path:path}", tags=["Static"])
@app.get("/edugate/js/{file_path:path}", tags=["Static"])
async def serve_js(file_path: str):
    landing_js = os.path.join(os.path.dirname(__file__), "static", "landing", "js", file_path)
    admin_js = os.path.join(os.path.dirname(__file__), "static", "admin", "js", file_path)
    if os.path.exists(landing_js) and os.path.isfile(landing_js):
        return FileResponse(landing_js, media_type="application/javascript; charset=utf-8")
    if os.path.exists(admin_js) and os.path.isfile(admin_js):
        return FileResponse(admin_js, media_type="application/javascript; charset=utf-8")
    raise HTTPException(status_code=404, detail="JS not found")


def render_admin_panel() -> str:
    admin_dir = os.path.join(os.path.dirname(__file__), "static", "admin")
    template_path = os.path.join(admin_dir, "template.html")
    index_path = os.path.join(admin_dir, "index.html")

    if not os.path.exists(template_path):
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>EDUGATE Admin Panel topilmadi</h1>"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    def replace_include(match):
        rel = match.group(1).strip()
        comp_path = os.path.join(admin_dir, rel)
        if os.path.exists(comp_path):
            with open(comp_path, "r", encoding="utf-8") as cf:
                return cf.read()
        return f"<!-- Missing component: {rel} -->"

    pattern = re.compile(r"<!--\s*include:\s*([a-zA-Z0-9_\-\./]+)\s*-->")
    return pattern.sub(replace_include, content)


@app.get("/admin", response_class=HTMLResponse, tags=["Admin Panel"])
@app.get("/admin/", response_class=HTMLResponse, tags=["Admin Panel"])
async def serve_admin_panel():
    html_content = render_admin_panel()
    response = HTMLResponse(content=html_content)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "sqlite" if settings.USE_SQLITE else "postgresql"
    }
