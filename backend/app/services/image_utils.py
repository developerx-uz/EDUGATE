import base64
import hashlib
import os
import uuid
from typing import Tuple

STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB


def _detect_image_ext(data: bytes) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    raise ValueError("Faqat JPEG, PNG yoki WEBP formatidagi haqiqiy rasm yuklash mumkin.")


def save_base64_image(
    image_base64: str,
    subfolder: str,
    filename_prefix: str,
    max_bytes: int = MAX_IMAGE_BYTES,
) -> Tuple[str, str]:
    """Validate and store a base64 image under static/uploads/{subfolder}.
    Returns (relative_url_path, sha256_descriptor).
    """
    if not image_base64 or not isinstance(image_base64, str):
        raise ValueError("Rasm ma'lumoti bo'sh.")

    raw_b64 = image_base64.strip()
    if "base64," in raw_b64:
        raw_b64 = raw_b64.split("base64,", 1)[1]

    try:
        img_bytes = base64.b64decode(raw_b64, validate=True)
    except Exception as exc:
        raise ValueError("Base64 rasm formati noto'g'ri.") from exc

    if not img_bytes:
        raise ValueError("Rasm fayli bo'sh.")
    if len(img_bytes) > max_bytes:
        raise ValueError("Rasm hajmi 5 MB dan oshmasligi kerak.")

    ext = _detect_image_ext(img_bytes)
    safe_prefix = "".join(c for c in filename_prefix if c.isalnum() or c in ("_", "-"))[:40] or "img"
    filename = f"{safe_prefix}_{uuid.uuid4().hex[:8]}{ext}"

    upload_dir = os.path.realpath(os.path.join(STATIC_DIR, "uploads", subfolder))
    uploads_root = os.path.realpath(os.path.join(STATIC_DIR, "uploads"))
    if os.path.commonpath([uploads_root, upload_dir]) != uploads_root:
        raise ValueError("Noto'g'ri saqlash papkasi.")

    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.write(img_bytes)

    digest = hashlib.sha256(img_bytes).hexdigest()[:24]
    rel_path = f"/static/uploads/{subfolder}/{filename}"
    return rel_path, f"img_sha256_{digest}"
