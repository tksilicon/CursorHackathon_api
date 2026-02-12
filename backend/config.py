"""Configuration from environment variables."""
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "rentshield")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "uploads"))

# Allowed image types and max size (bytes)
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

VOUCHER_TYPES = ("cinema_10", "coffee_5", "amazon_10")
DEFAULT_VOUCHER_TYPE = "amazon_10"
