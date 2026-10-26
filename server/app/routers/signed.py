"""Приватный эндпоинт с JWT, подписанным HS256 слабым секретом."""

from fastapi import APIRouter, Header

from app.schemas import TokenResponse
from app.security import extract_bearer, verify_hs256_jwt

router = APIRouter(tags=["private"])


@router.get(
    "/private/signed",
    response_model=TokenResponse,
    summary="Приватный, JWT подписан HS256 (слабый секрет)",
)
def private_signed(authorization: str | None = Header(default=None)) -> TokenResponse:
    """Проверяет HS256 слабым общим секретом из ``config.SECRET_KEY``."""
    token = extract_bearer(authorization)
    claims = verify_hs256_jwt(token)
    return TokenResponse(
        ok=True,
        endpoint="/private/signed",
        claims=claims,
        note="HS256 проверен слабым секретом, который извлекается из клиента.",
    )
