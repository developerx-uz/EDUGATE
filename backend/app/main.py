import logging
import os
import re
import time
from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.core.redis import debounce_manager
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.api.v1.api import api_router
from app.api.v1.endpoints.orders import create_lead_order_record
from app.schemas.parent_order import LeadOrderCreate

logger = logging.getLogger("edugate.main")


async def _run_auto_migrations(conn):
    """Dialect-safe column migrations for both SQLite and PostgreSQL."""
    dialect = conn.dialect.name
    migrations = [
        ("students", "pinfl", "VARCHAR(14)"),
        ("students", "birth_cert_number", "VARCHAR(50)"),
        ("students", "gender", "VARCHAR(1)"),
        ("users", "role", "VARCHAR(50) DEFAULT 'SUPERADMIN'"),
        ("users", "school_id", "VARCHAR(36)"),
    ]

    for table, col, col_def in migrations:
        try:
            if dialect == "sqlite":
                rows = (await conn.execute(text(f"PRAGMA table_info({table})"))).all()
                existing_cols = {r[1] for r in rows}
                if col not in existing_cols:
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def};"))
            else:
                await conn.execute(
                    text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_def};")
                )
        except Exception as exc:
            logger.warning(f"Auto-migration skipped ({table}.{col}): {exc}")

    try:
        await conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_users_school_id "
                "ON users (school_id) WHERE school_id IS NOT NULL;"
            )
        )
    except Exception as exc:
        logger.warning(f"Index uq_users_school_id creation skipped: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.DEBUG and "super-secret" in settings.SECRET_KEY:
        logger.warning("XAVFSIZLIK OGOHLANTIRISHI: Production rejimida standart SECRET_KEY ishlatilmoqda!")

    # Dastur ishga tushganda: Baza jadvallarini tekshirish/yaratish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _run_auto_migrations(conn)

    # Initial foydalanuvchilar: Superadmin va Xalq Ta'limi
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).filter(User.username == "admin"))
        if not res.scalar_one_or_none():
            session.add(
                User(
                    username="admin",
                    email="admin@edugate.uz",
                    full_name="Viloyat va Shahar Hokimligi Superadmini",
                    hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                    role=UserRole.SUPERADMIN,
                    is_superadmin=True,
                    is_active=True,
                )
            )
            await session.commit()

        res_xt = await session.execute(select(User).filter(User.username == "xalq_talimi"))
        if not res_xt.scalar_one_or_none():
            session.add(
                User(
                    username="xalq_talimi",
                    email="monitoring@edugate.uz",
                    full_name="Xalq Ta'limi Vazirligi (Monitoring Inspeksiya)",
                    hashed_password=get_password_hash(settings.INITIAL_MINISTRY_PASSWORD),
                    role=UserRole.MINISTRY_VIEWER,
                    is_superadmin=False,
                    is_active=True,
                )
            )
            await session.commit()

    await debounce_manager.initialize()
    yield
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
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    app.mount("/edugate/static", StaticFiles(directory=static_dir), name="edugate_static")

landing_dir = os.path.join(os.path.dirname(__file__), "static", "landing")
landing_assets_dir = os.path.join(landing_dir, "assets")

CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


def _resolve_safe_path(base_dir: str, rel_path: str) -> str | None:
    real_base = os.path.realpath(base_dir)
    real_target = os.path.realpath(os.path.join(real_base, rel_path))
    if os.path.commonpath([real_base, real_target]) != real_base:
        return None
    if os.path.exists(real_target) and os.path.isfile(real_target):
        return real_target
    return None


# Marshrutlar
app.include_router(api_router, prefix=settings.API_V1_STR)
if not settings.API_V1_STR.startswith("/edugate"):
    app.include_router(api_router, prefix="/edugate" + settings.API_V1_STR)


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/index.html", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/edugate", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/edugate/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
@app.api_route("/edugate/index.html", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Public Portal"])
async def serve_landing(request: Request):
    host = request.headers.get("host", "").lower()
    if host.startswith(("journal.", "school.", "maktab.")):
        return HTMLResponse(content=render_admin_html(portal_mode="school"), headers=CACHE_HEADERS)
    if host.startswith(("edu.", "monitoring.", "mmtv.")):
        return HTMLResponse(content=render_admin_html(portal_mode="monitoring"), headers=CACHE_HEADERS)
    if host.startswith("admin."):
        return HTMLResponse(content=render_admin_html(portal_mode="admin"), headers=CACHE_HEADERS)

    landing_index = os.path.join(landing_dir, "index.html")
    if os.path.exists(landing_index):
        with open(landing_index, "r", encoding="utf-8") as f:
            content = f.read()
        ts = str(int(time.time()))
        content = re.sub(r"(\.(?:css|js))\?[tv]=[^\"\'\s>]+", r"\g<1>?t=" + ts, content)
        return HTMLResponse(content=content, headers=CACHE_HEADERS)
    return HTMLResponse("<h1>EDUGATE — Davomat va Xavfsizlik Ekotizimi</h1>")


@app.get("/Orlan-logo.png", tags=["Public Portal"])
@app.get("/edugate/Orlan-logo.png", tags=["Public Portal"])
async def serve_landing_logo():
    logo_file = _resolve_safe_path(landing_dir, "Orlan-logo.png")
    if logo_file:
        return FileResponse(logo_file, media_type="image/png", headers=CACHE_HEADERS)
    return HTMLResponse(status_code=404)


@app.get("/assets/{file_path:path}", tags=["Public Portal"])
@app.get("/edugate/assets/{file_path:path}", tags=["Public Portal"])
async def serve_landing_asset(file_path: str):
    full_path = _resolve_safe_path(landing_assets_dir, file_path)
    if full_path:
        media_type = None
        if full_path.endswith(".css"):
            media_type = "text/css; charset=utf-8"
        elif full_path.endswith(".js"):
            media_type = "application/javascript; charset=utf-8"
        return FileResponse(full_path, media_type=media_type, headers=CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/css/{file_path:path}", tags=["Static"])
@app.get("/edugate/css/{file_path:path}", tags=["Static"])
async def serve_css(file_path: str):
    for root in (os.path.join(landing_dir, "css"), os.path.join(static_dir, "admin", "css")):
        full_path = _resolve_safe_path(root, file_path)
        if full_path:
            return FileResponse(full_path, media_type="text/css; charset=utf-8", headers=CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="CSS not found")


@app.get("/js/{file_path:path}", tags=["Static"])
@app.get("/edugate/js/{file_path:path}", tags=["Static"])
async def serve_js(file_path: str):
    for root in (os.path.join(landing_dir, "js"), os.path.join(static_dir, "admin", "js")):
        full_path = _resolve_safe_path(root, file_path)
        if full_path:
            return FileResponse(full_path, media_type="application/javascript; charset=utf-8", headers=CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="JS not found")


@app.get("/presentation", response_class=HTMLResponse, tags=["Presentation"])
@app.get("/presentation.html", response_class=HTMLResponse, tags=["Presentation"])
@app.get("/edugate/presentation", response_class=HTMLResponse, tags=["Presentation"])
@app.get("/edugate/presentation.html", response_class=HTMLResponse, tags=["Presentation"])
async def serve_presentation():
    pres_file = _resolve_safe_path(landing_dir, "presentation.html")
    if pres_file:
        with open(pres_file, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, headers=CACHE_HEADERS)
    return HTMLResponse("<h1>Prezentatsiya topilmadi</h1>", status_code=404)


def render_admin_html(portal_mode: str = "admin") -> str:
    admin_dir = os.path.join(static_dir, "admin")
    template_path = os.path.join(admin_dir, "template.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        def replacer(match):
            inc_file = match.group(1).strip()
            full_path = _resolve_safe_path(admin_dir, inc_file)
            if full_path:
                with open(full_path, "r", encoding="utf-8") as inc_f:
                    return inc_f.read()
            return f"<!-- missing {inc_file} -->"

        content = re.sub(r"<!--\s*include:\s*([^\s>]+)\s*-->", replacer, template)
        ts = str(int(time.time()))
        content = re.sub(r"(\.(?:css|js))\?[tv]=[^\"\'\s>]+", r"\g<1>?t=" + ts, content)

        portal_script = f'<script>window.EDUGATE_INITIAL_PORTAL = "{portal_mode}";</script>'
        if "</head>" in content:
            content = content.replace("</head>", f"    {portal_script}\n</head>")
        return content

    admin_index = os.path.join(admin_dir, "index.html")
    if os.path.exists(admin_index):
        with open(admin_index, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Admin panel topilmadi</h1>"


@app.api_route("/manifest.json", methods=["GET", "HEAD"], tags=["PWA"])
@app.api_route("/edugate/manifest.json", methods=["GET", "HEAD"], tags=["PWA"])
async def serve_manifest():
    manifest_file = _resolve_safe_path(os.path.join(static_dir, "admin"), "manifest.json")
    if manifest_file:
        return FileResponse(manifest_file, media_type="application/manifest+json", headers=CACHE_HEADERS)
    return JSONResponse({"name": "EDUGATE", "short_name": "EDUGATE"})


@app.api_route("/sw.js", methods=["GET", "HEAD"], tags=["PWA"])
@app.api_route("/edugate/sw.js", methods=["GET", "HEAD"], tags=["PWA"])
async def serve_service_worker():
    sw_file = _resolve_safe_path(os.path.join(static_dir, "admin"), "sw.js")
    if sw_file:
        headers = dict(CACHE_HEADERS)
        headers["Service-Worker-Allowed"] = "/"
        return FileResponse(sw_file, media_type="application/javascript", headers=headers)
    return Response(content="// SW not found", media_type="application/javascript")


@app.api_route("/static/admin/icons/{icon_name}", methods=["GET", "HEAD"], tags=["PWA"])
@app.api_route("/edugate/static/admin/icons/{icon_name}", methods=["GET", "HEAD"], tags=["PWA"])
async def serve_pwa_icon(icon_name: str):
    icon_path = _resolve_safe_path(os.path.join(static_dir, "admin", "icons"), icon_name)
    if icon_path:
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
async def serve_admin(request: Request):
    return HTMLResponse(content=render_admin_html(portal_mode="admin"), headers=CACHE_HEADERS)


@app.api_route("/edu", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/edu/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/monitoring", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/monitoring/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/mmtv", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/mmtv/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/edugate/edu", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/edugate/edu/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/edugate/monitoring", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/edugate/monitoring/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/edugate/mmtv", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
@app.api_route("/edugate/mmtv/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["Ministry Portal"])
async def serve_ministry(request: Request):
    return HTMLResponse(content=render_admin_html(portal_mode="monitoring"), headers=CACHE_HEADERS)


@app.api_route("/journal", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/journal/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/school", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/school/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/maktab", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/maktab/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/edugate/journal", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/edugate/journal/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/edugate/school", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/edugate/school/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/edugate/maktab", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
@app.api_route("/edugate/maktab/", methods=["GET", "HEAD"], response_class=HTMLResponse, tags=["School Portal"])
async def serve_school(request: Request):
    return HTMLResponse(content=render_admin_html(portal_mode="school"), headers=CACHE_HEADERS)


@app.post("/api/contact", tags=["Contact"])
@app.post("/edugate/api/contact", tags=["Contact"])
async def submit_contact_lead(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    try:
        data = await request.json()
    except Exception:
        data = {}

    if data.get("phone") or data.get("phone_number"):
        lead_payload = LeadOrderCreate(
            full_name=data.get("full_name") or data.get("contact_name"),
            phone=data.get("phone") or data.get("phone_number"),
            region=data.get("region"),
            school_info=data.get("school_info") or data.get("school_name"),
            message=data.get("message"),
            source="landing_contact",
        )
        lead = await create_lead_order_record(db, lead_payload, background_tasks)
        return {
            "status": "success",
            "id": lead.id,
            "message": "Arizangiz qabul qilindi! Tez orada mutaxassisimiz bog'lanadi.",
        }

    raise HTTPException(status_code=400, detail="Telefon raqami kiritilishi shart.")


@app.get("/health", tags=["Health"])
@app.get("/edugate/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "online" if db_ok else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "type": "sqlite" if settings.USE_SQLITE else "postgresql",
            "connected": db_ok,
        },
        "cache": debounce_manager.get_status(),
    }
