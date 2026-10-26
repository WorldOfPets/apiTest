"""Эндпоинт только для админа с неподписанным JWT (``alg=none``)."""

from fastapi import APIRouter, Header

from app.schemas import TokenResponse
from app.security import decode_none_jwt, extract_bearer, require_admin

router = APIRouter(tags=["private"])


@router.get(
    "/private/admin",
    response_model=TokenResponse,
    summary="Только для админа, неподписанный JWT (alg=none)",
)
def private_admin(authorization: str | None = Header(default=None)) -> TokenResponse:
    """Требует ``role == 'admin'``, но по-прежнему доверяет неподписанному JWT."""
    token = extract_bearer(authorization)
    header, claims = decode_none_jwt(token)
    require_admin(claims)
    return TokenResponse(
        ok=True,
        endpoint="/private/admin",
        header=header,
        claims=claims,
        note="Админский доступ выдан по неподписанному JWT. Подмените claim role!",
    )
