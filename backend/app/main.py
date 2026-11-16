import os
import re
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse, Response
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


root_path = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="EDUGATE — Maktablar uchun Face ID, Kameralar va Turniketlar bilan ishlovchi aqlli davomat tizimi yadrosi.",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
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
    app.mount("/edugate/static", StaticFiles(directory=static_dir), name="edugate_static")

landing_dir = os.path.join(os.path.dirname(__file__), "static", "landing")
landing_assets_dir = os.path.join(landing_dir, "assets")

# Anti-Cache global headers for all static files and assets
CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0"
}


# Marshrutlar
app.include_router(api_router, prefix=settings.API_V1_STR)
if not settings.API_V1_STR.startswith("/edugate"):
    app.include_router(api_router, prefix="/edugate" + settings.API_V1_STR)


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/index.html", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/edugate", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/edugate/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/edugate/index.html", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
async def serve_landing():
    landing_index = os.path.join(os.path.dirname(__file__), "static", "landing", "index.html")
    if os.path.exists(landing_index):
        with open(landing_index, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Har safar sahifa ochilganda yoki refresh qilinganda avtomatik yangi timestamp qo'yish
        # Natijada brauzer hech qachon eski keshni ishlatmaydi va har doim yangi fayllarni yuklaydi
        import time, re
        ts = str(int(time.time()))
        content = re.sub(r"(\.(?:css|js))\?[tv]=[^\"\'\s>]+", r"\g<1>?t=" + ts, content)
        
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
        return FileResponse(logo_file, media_type="image/png", headers=CACHE_HEADERS)
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
        return FileResponse(full_path, media_type=media_type, headers=CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/css/{file_path:path}", tags=["Static"])
@app.get("/edugate/css/{file_path:path}", tags=["Static"])
async def serve_css(file_path: str):
    landing_css = os.path.join(os.path.dirname(__file__), "static", "landing", "css", file_path)
    admin_css = os.path.join(os.path.dirname(__file__), "static", "admin", "css", file_path)
    if os.path.exists(landing_css) and os.path.isfile(landing_css):
        return FileResponse(landing_css, media_type="text/css; charset=utf-8", headers=CACHE_HEADERS)
    if os.path.exists(admin_css) and os.path.isfile(admin_css):
        return FileResponse(admin_css, media_type="text/css; charset=utf-8", headers=CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="CSS not found")


@app.get("/js/{file_path:path}", tags=["Static"])
@app.get("/edugate/js/{file_path:path}", tags=["Static"])
async def serve_js(file_path: str):
    landing_js = os.path.join(os.path.dirname(__file__), "static", "landing", "js", file_path)
    admin_js = os.path.join(os.path.dirname(__file__), "static", "admin", "js", file_path)
    if os.path.exists(landing_js) and os.path.isfile(landing_js):
        return FileResponse(landing_js, media_type="application/javascript; charset=utf-8", headers=CACHE_HEADERS)
    if os.path.exists(admin_js) and os.path.isfile(admin_js):
        return FileResponse(admin_js, media_type="application/javascript; charset=utf-8", headers=CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="JS not found")


@app.get("/presentation", response_class=HTMLResponse, tags=["Presentation"])
@app.get("/presentation.html", response_class=HTMLResponse, tags=["Presentation"])
@app.get("/edugate/presentation", response_class=HTMLResponse, tags=["Presentation"])
@app.get("/edugate/presentation.html", response_class=HTMLResponse, tags=["Presentation"])
async def serve_presentation():
    pres_file = os.path.join(os.path.dirname(__file__), "static", "landing", "presentation.html")
    if os.path.exists(pres_file):
        with open(pres_file, "r", encoding="utf-8") as f:
            content = f.read()
        response = HTMLResponse(content=content)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        return response
    return HTMLResponse("<h1>Prezentatsiya topilmadi</h1>", status_code=404)


def render_admin_html() -> str:
    admin_dir = os.path.join(os.path.dirname(__file__), "static", "admin")
    template_path = os.path.join(admin_dir, "template.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        def replacer(match):
            inc_file = match.group(1).strip()
            full_path = os.path.join(admin_dir, inc_file)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as inc_f:
                    return inc_f.read()
            return f"<!-- missing {inc_file} -->"

        content = re.sub(r"<!--\s*include:\s*([^\s>]+)\s*-->", replacer, template)
        ts = str(int(time.time()))
        content = re.sub(r"(\.(?:css|js))\?[tv]=[^\"\'\s>]+", r"\g<1>?t=" + ts, content)
        return content

    admin_index = os.path.join(admin_dir, "index.html")
    if os.path.exists(admin_index):
        with open(admin_index, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Admin panel topilmadi</h1>"


@app.api_route("/manifest.json", methods=["GET", "HEAD"], tags=["PWA"])
@app.api_route("/edugate/manifest.json", methods=["GET", "HEAD"], tags=["PWA"])
async def serve_manifest():
    manifest_file = os.path.join(os.path.dirname(__file__), "static", "admin", "manifest.json")
    if os.path.exists(manifest_file):
        return FileResponse(manifest_file, media_type="application/manifest+json", headers=CACHE_HEADERS)
    return JSONResponse({"name": "EDUGATE", "short_name": "EDUGATE"})


@app.api_route("/sw.js", methods=["GET", "HEAD"], tags=["PWA"])
@app.api_route("/edugate/sw.js", methods=["GET", "HEAD"], tags=["PWA"])
async def serve_service_worker():
    sw_file = os.path.join(os.path.dirname(__file__), "static", "admin", "sw.js")
    if os.path.exists(sw_file):
        headers = dict(CACHE_HEADERS)
        headers["Service-Worker-Allowed"] = "/"
        return FileResponse(sw_file, media_type="application/javascript", headers=headers)
    return Response(content="// SW not found", media_type="application/javascript")


@app.api_route("/static/admin/icons/{icon_name}", methods=["GET", "HEAD"], tags=["PWA"])
@app.api_route("/edugate/static/admin/icons/{icon_name}", methods=["GET", "HEAD"], tags=["PWA"])
async def serve_pwa_icon(icon_name: str):
    icon_path = os.path.join(os.path.dirname(__file__), "static", "admin", "icons", icon_name)
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/png", headers=CACHE_HEADERS)
    return Response(status_code=404)


# Block and disable all documentation endpoints for confidential security
@app.api_route("/docs", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/docs/{rest_of_path:path}", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/edugate/docs", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/edugate/docs/{rest_of_path:path}", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/redoc", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/redoc/{rest_of_path:path}", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/edugate/redoc", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/edugate/redoc/{rest_of_path:path}", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/openapi.json", methods=["GET", "HEAD", "POST"], include_in_schema=False)
@app.api_route("/edugate/openapi.json", methods=["GET", "HEAD", "POST"], include_in_schema=False)
async def block_docs(rest_of_path: str = ""):
    raise HTTPException(status_code=404, detail="Not Found")


@app.api_route("/admin", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Admin Portal"])
@app.api_route("/admin/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Admin Portal"])
@app.api_route("/edugate/admin", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Admin Portal"])
@app.api_route("/edugate/admin/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Admin Portal"])
async def serve_admin():
    content = render_admin_html()
    response = HTMLResponse(content=content)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response



@app.post("/api/contact", tags=["Contact"])
@app.post("/edugate/api/contact", tags=["Contact"])
async def submit_contact_lead(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    return {
        "status": "success",
        "message": "Arizangiz qabul qilindi! Tez orada mutaxassisimiz bog'lanadi.",
        "data": data
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "sqlite" if settings.USE_SQLITE else "postgresql"
    }
