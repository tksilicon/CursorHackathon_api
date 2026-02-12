"""Property review API: create, list, get, upload photos, verdict."""
from datetime import datetime
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query, status

from backend.config import ALLOWED_IMAGE_EXTENSIONS, DEFAULT_VOUCHER_TYPE, MAX_FILE_SIZE_BYTES
from backend.db import get_db
from backend.dependencies import require_admin, require_landlord, require_tenant, require_any_role
from backend.models import (
    CreateReviewRequest,
    CreateReviewResponse,
    PhotoEntry,
    PropertyReviewResponse,
    VerdictRequest,
)
from backend.storage import allowed_file, save_upload

router = APIRouter(prefix="/api/property-reviews", tags=["property-reviews"])


def _oid(s: str) -> ObjectId:
    if not ObjectId.is_valid(s):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")
    return ObjectId(s)


def _review_to_response(doc: dict) -> PropertyReviewResponse:
    def photo_entries(arr: list) -> list[PhotoEntry]:
        return [
            PhotoEntry(url=e["url"], uploadedAt=e["uploadedAt"], uploadedBy=str(e["uploadedBy"]))
            for e in (arr or [])
        ]
    return PropertyReviewResponse(
        id=str(doc["_id"]),
        tenantId=str(doc["tenantId"]),
        propertyId=str(doc["propertyId"]) if doc.get("propertyId") else None,
        landlordId=str(doc["landlordId"]),
        landlordPhotos=photo_entries(doc.get("landlordPhotos") or []),
        tenantPhotos=photo_entries(doc.get("tenantPhotos") or []),
        landlordNote=doc.get("landlordNote"),
        status=doc.get("status", "pending_admin_review"),
        adminVerdict=doc.get("adminVerdict"),
        reviewedById=str(doc["reviewedById"]) if doc.get("reviewedById") else None,
        reviewedAt=doc.get("reviewedAt"),
        voucherId=str(doc["voucherId"]) if doc.get("voucherId") else None,
        createdAt=doc["createdAt"],
        updatedAt=doc["updatedAt"],
    )


@router.post("", response_model=CreateReviewResponse)
def create_review(
    body: CreateReviewRequest,
    landlord_id: Annotated[str, Depends(require_landlord)],
    db=Depends(get_db),
):
    """Create a review for a tenant. Body: tenantId (required), optional landlordNote."""
    tenant_oid = _oid(body.tenantId)
    now = datetime.utcnow()
    # propertyId optional; could be derived from tenant assignment if you have a tenancies collection
    doc = {
        "tenantId": tenant_oid,
        "propertyId": None,
        "landlordId": ObjectId(landlord_id),
        "landlordPhotos": [],
        "tenantPhotos": [],
        "landlordNote": body.landlordNote,
        "status": "pending_admin_review",
        "createdAt": now,
        "updatedAt": now,
    }
    ins = db.property_reviews.insert_one(doc)
    return CreateReviewResponse(propertyReviewId=str(ins.inserted_id))


def _can_access_review(doc: dict, user_id: str, role: str) -> bool:
    if role == "admin":
        return True
    if role == "landlord":
        return str(doc.get("landlordId")) == user_id
    if role == "tenant":
        return str(doc.get("tenantId")) == user_id
    return False


@router.get("", response_model=list[PropertyReviewResponse])
def list_reviews(
    tenantId: str | None = None,
    propertyId: str | None = None,
    status_query: str | None = Query(None, alias="status"),
    user_and_role: Annotated[tuple[str, str], Depends(require_any_role)] = None,
    db=Depends(get_db),
):
    """List reviews. Landlord: own; tenant: for them; admin: all. Query: tenantId, propertyId, status."""
    user_id, role = user_and_role
    query = {}
    if role == "landlord":
        query["landlordId"] = ObjectId(user_id)
    elif role == "tenant":
        query["tenantId"] = ObjectId(user_id)
    if tenantId:
        query["tenantId"] = _oid(tenantId)
    if propertyId:
        query["propertyId"] = _oid(propertyId)
    if status_query:
        query["status"] = status_query
    cursor = db.property_reviews.find(query).sort("createdAt", -1)
    docs = list(cursor)
    return [_review_to_response(d) for d in docs]


@router.get("/{id}", response_model=PropertyReviewResponse)
def get_review(
    id: str,
    user_and_role: Annotated[tuple[str, str], Depends(require_any_role)] = None,
    db=Depends(get_db),
):
    """Get one review. Access: landlord (own), tenant (for them), admin (all)."""
    user_id, role = user_and_role
    doc = db.property_reviews.find_one({"_id": _oid(id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if not _can_access_review(doc, user_id, role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return _review_to_response(doc)


def _validate_photo(file: UploadFile) -> bytes:
    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}",
        )
    content = file.file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max {MAX_FILE_SIZE_BYTES // (1024*1024)} MB",
        )
    return content


@router.post("/{id}/photos", status_code=status.HTTP_200_OK)
def upload_landlord_photos(
    id: str,
    files: Annotated[list[UploadFile], File()],
    landlord_id: Annotated[str, Depends(require_landlord)],
    db=Depends(get_db),
):
    """Landlord uploads one or more photos. Multipart form: files."""
    doc = db.property_reviews.find_one({"_id": _oid(id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if str(doc["landlordId"]) != landlord_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your review")
    if doc.get("status") != "pending_admin_review":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review no longer pending")
    photos = list(doc.get("landlordPhotos") or [])
    now = datetime.utcnow()
    for file in files:
        content = _validate_photo(file)
        url = save_upload(content, file.filename or "photo.jpg")
        photos.append({"url": url, "uploadedAt": now, "uploadedBy": landlord_id})
    db.property_reviews.update_one(
        {"_id": _oid(id)},
        {"$set": {"landlordPhotos": photos, "updatedAt": now}},
    )
    return {"uploaded": len(files)}


@router.post("/{id}/tenant-photos", status_code=status.HTTP_200_OK)
def upload_tenant_photos(
    id: str,
    files: Annotated[list[UploadFile], File()],
    tenant_id: Annotated[str, Depends(require_tenant)],
    db=Depends(get_db),
):
    """Tenant uploads photos for a review created for them."""
    doc = db.property_reviews.find_one({"_id": _oid(id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if str(doc["tenantId"]) != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Review not for you")
    if doc.get("status") != "pending_admin_review":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Review no longer pending")
    photos = list(doc.get("tenantPhotos") or [])
    now = datetime.utcnow()
    for file in files:
        content = _validate_photo(file)
        url = save_upload(content, file.filename or "photo.jpg")
        photos.append({"url": url, "uploadedAt": now, "uploadedBy": tenant_id})
    db.property_reviews.update_one(
        {"_id": _oid(id)},
        {"$set": {"tenantPhotos": photos, "updatedAt": now}},
    )
    return {"uploaded": len(files)}


@router.post("/{id}/verdict", status_code=status.HTTP_200_OK)
def set_verdict(
    id: str,
    body: VerdictRequest,
    admin_id: Annotated[str, Depends(require_admin)],
    db=Depends(get_db),
):
    """Admin sets thumbs_up or thumbs_down. If thumbs_up, optional voucherType (default amazon_10); backend generates 16-digit code. Idempotent."""
    doc = db.property_reviews.find_one({"_id": _oid(id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    if doc.get("adminVerdict") is not None:
        return {"status": doc["status"], "message": "Verdict already set"}
    now = datetime.utcnow()
    if body.verdict == "thumbs_down":
        db.property_reviews.update_one(
            {"_id": _oid(id)},
            {"$set": {"status": "rejected", "adminVerdict": "thumbs_down", "reviewedById": ObjectId(admin_id), "reviewedAt": now, "updatedAt": now}},
        )
        return {"status": "rejected"}
    voucher_type = body.voucherType or DEFAULT_VOUCHER_TYPE
    if voucher_type not in ("cinema_10", "coffee_5", "amazon_10"):
        voucher_type = DEFAULT_VOUCHER_TYPE
    import secrets
    code = "".join(secrets.choice("0123456789") for _ in range(16))
    voucher_doc = {
        "tenantId": doc["tenantId"],
        "propertyReviewId": _oid(id),
        "voucherType": voucher_type,
        "voucherCode": code,
        "issuedById": ObjectId(admin_id),
        "issuedAt": now,
        "status": "issued",
    }
    ins = db.vouchers.insert_one(voucher_doc)
    db.property_reviews.update_one(
        {"_id": _oid(id)},
        {"$set": {
            "status": "approved",
            "adminVerdict": "thumbs_up",
            "reviewedById": ObjectId(admin_id),
            "reviewedAt": now,
            "voucherId": ins.inserted_id,
            "updatedAt": now,
        }},
    )
    return {"status": "approved", "voucherId": str(ins.inserted_id)}
