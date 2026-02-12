"""Vouchers API: list for tenant or admin."""
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends

from backend.db import get_db
from backend.dependencies import require_any_role
from backend.models import VoucherResponse

router = APIRouter(prefix="/api/vouchers", tags=["vouchers"])

VOUCHER_LABELS = {
    "cinema_10": "Cinema £10",
    "coffee_5": "Coffee £5",
    "amazon_10": "Amazon £10",
}


def _voucher_to_response(doc: dict) -> VoucherResponse:
    return VoucherResponse(
        id=str(doc["_id"]),
        tenantId=str(doc["tenantId"]),
        propertyReviewId=str(doc["propertyReviewId"]),
        voucherType=doc["voucherType"],
        voucherCode=doc["voucherCode"],
        voucherTypeLabel=VOUCHER_LABELS.get(doc["voucherType"], doc["voucherType"]),
        issuedById=str(doc["issuedById"]),
        issuedAt=doc["issuedAt"],
        status=doc.get("status", "issued"),
    )


@router.get("", response_model=list[VoucherResponse])
def list_vouchers(
    user_and_role: Annotated[tuple[str, str], Depends(require_any_role)],
    db=Depends(get_db),
):
    """Tenant: list own vouchers. Admin: list all vouchers."""
    user_id, role = user_and_role
    if role == "admin":
        docs = db.vouchers.find({}).sort("issuedAt", -1)
    else:
        docs = db.vouchers.find({"tenantId": ObjectId(user_id)}).sort("issuedAt", -1)
    return [_voucher_to_response(d) for d in docs]
