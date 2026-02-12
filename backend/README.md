# Property Photo Review API

Python FastAPI service for property photo review and voucher issuance. Implements [specs/property-photo-review.md](../specs/property-photo-review.md).

## Setup

1. From the **project root** (CursorHackathon), create and use a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Environment variables (local env or `.env`):

   - `MONGODB_URI` — MongoDB connection string (e.g. `mongodb://localhost:27017` or Atlas URI).
   - `DB_NAME` — Database name (default: `rentshield`).
   - `UPLOAD_DIR` — Directory for uploaded photos (default: `uploads` under project root).

3. Run:

   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   API: `http://localhost:8000`  
   Docs: `http://localhost:8000/docs`

## Auth

The API does not issue tokens. It expects the **user management service** (or gateway) to set:

- **`X-User-Id`** — Current user id (e.g. MongoDB `_id` hex string).
- **`X-Role`** — One of `admin`, `landlord`, `tenant`.

Missing or invalid headers return 401; role checks return 403.

## Endpoints

| Method | Path | Role | Description |
|--------|------|------|-------------|
| POST | `/api/property-reviews` | landlord | Create review; body: `tenantId`, optional `landlordNote`. |
| POST | `/api/property-reviews/{id}/photos` | landlord | Upload landlord photos (multipart). |
| POST | `/api/property-reviews/{id}/tenant-photos` | tenant | Upload tenant photos (multipart). |
| GET | `/api/property-reviews` | landlord, tenant, admin | List reviews (query: `tenantId`, `propertyId`, `status`). |
| GET | `/api/property-reviews/{id}` | landlord, tenant, admin | Get one review. |
| POST | `/api/property-reviews/{id}/verdict` | admin | Set `thumbs_up` or `thumbs_down`; if thumbs up, optional `voucherType` (default `amazon_10`). |
| GET | `/api/vouchers` | tenant, admin | Tenant: own vouchers; admin: all. |

Uploaded images are stored under `UPLOAD_DIR` and served at `/uploads/{filename}`.

## Voucher types

- `cinema_10` — Cinema £10  
- `coffee_5` — Coffee £5  
- `amazon_10` — Amazon £10 (default when admin does not specify)

Voucher codes are a random 16-digit string; display in UI as `1234-5678-9012-3456`.
