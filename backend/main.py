"""Property Photo Review API — FastAPI app."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.config import UPLOAD_DIR
from backend.routers import property_reviews, vouchers

app = FastAPI(
    title="Property Photo Review API",
    description="Review management and voucher issuance for RentShield (spec: specs/property-photo-review.md)",
    version="1.0.0",
)

app.include_router(property_reviews.router)
app.include_router(vouchers.router)

# Serve uploaded photos at /uploads
upload_path = Path(UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}
