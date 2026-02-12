"""Auth and request dependencies. Trusts X-User-Id and X-Role from user management layer."""
from typing import Annotated, Literal

from fastapi import Depends, Header, HTTPException, status

Role = Literal["admin", "landlord", "tenant"]


def get_current_user_id(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> str:
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    return x_user_id


def get_current_role(
    x_role: Annotated[str | None, Header(alias="X-Role")] = None,
) -> Role:
    if not x_role or x_role not in ("admin", "landlord", "tenant"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-Role header",
        )
    return x_role  # type: ignore


def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    role: Annotated[Role, Depends(get_current_role)],
) -> tuple[str, Role]:
    return user_id, role


def require_landlord(
    user_id: Annotated[str, Depends(get_current_user_id)],
    role: Annotated[Role, Depends(get_current_role)],
) -> str:
    if role != "landlord":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Landlord role required")
    return user_id


def require_tenant(
    user_id: Annotated[str, Depends(get_current_user_id)],
    role: Annotated[Role, Depends(get_current_role)],
) -> str:
    if role != "tenant":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant role required")
    return user_id


def require_admin(
    user_id: Annotated[str, Depends(get_current_user_id)],
    role: Annotated[Role, Depends(get_current_role)],
) -> str:
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user_id


def require_any_role(
    user_id: Annotated[str, Depends(get_current_user_id)],
    role: Annotated[Role, Depends(get_current_role)],
) -> tuple[str, Role]:
    return user_id, role
