"""Pydantic models for request/response."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# IDs are strings (hex) in API; we convert to/from ObjectId in services.
Verdict = Literal["thumbs_up", "thumbs_down"]
VoucherType = Literal["cinema_10", "coffee_5", "amazon_10"]


class CreateReviewRequest(BaseModel):
    tenantId: str
    landlordNote: str | None = None


class CreateReviewResponse(BaseModel):
    propertyReviewId: str


class VerdictRequest(BaseModel):
    verdict: Verdict
    voucherType: VoucherType | None = None  # default amazon_10 when verdict is thumbs_up


class PhotoEntry(BaseModel):
    url: str
    uploadedAt: datetime
    uploadedBy: str


class PropertyReviewResponse(BaseModel):
    id: str
    tenantId: str
    propertyId: str | None
    landlordId: str
    landlordPhotos: list[PhotoEntry] = Field(default_factory=list)
    tenantPhotos: list[PhotoEntry] = Field(default_factory=list)
    landlordNote: str | None
    status: str
    adminVerdict: str | None = None
    reviewedById: str | None = None
    reviewedAt: datetime | None = None
    voucherId: str | None = None
    createdAt: datetime
    updatedAt: datetime


class VoucherResponse(BaseModel):
    id: str
    tenantId: str
    propertyReviewId: str
    voucherType: str
    voucherCode: str  # 16 digits; frontend formats as 1234-5678-9012-3456
    voucherTypeLabel: str  # e.g. "Cinema £10"
    issuedById: str
    issuedAt: datetime
    status: str
