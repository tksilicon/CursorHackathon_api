"""Local file storage for uploaded photos."""
import os
import secrets
from pathlib import Path

from backend.config import UPLOAD_DIR, ALLOWED_IMAGE_EXTENSIONS, MAX_FILE_SIZE_BYTES


def ensure_upload_dir() -> Path:
    path = Path(UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def allowed_file(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def save_upload(file_content: bytes, filename: str) -> str:
    """Save file to UPLOAD_DIR; return URL path for DB (e.g. /uploads/abc123.jpg)."""
    ensure_upload_dir()
    ext = Path(filename).suffix.lower() or ".jpg"
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = ".jpg"
    name = secrets.token_hex(8) + ext
    path = Path(UPLOAD_DIR) / name
    path.write_bytes(file_content)
    return f"/uploads/{name}"
