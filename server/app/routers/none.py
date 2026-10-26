"""Приватный эндпоинт с неподписанным JWT (``alg=none``)."""

from fastapi import APIRouter, Header

from app.schemas import TokenResponse
from app.security import decode_none_jwt, extract_bearer

router = APIRouter(tags=["private"])


@router.get(
    "/private/none",
    response_model=TokenResponse,
    summary="Приватный, неподписанный JWT (alg=none)",
)
def private_none(authorization: str | None = Header(default=None)) -> TokenResponse:
    """Подпись игнорируется, поэтому принимается любой токен ``alg=none``."""
    token = extract_bearer(authorization)
    header, claims = decode_none_jwt(token)
    return TokenResponse(
        ok=True,
        endpoint="/private/none",
        header=header,
        claims=claims,
        note="Неподписанный JWT принят. Подпись никогда не проверялась.",
    )
