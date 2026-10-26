"""Приватный эндпоинт с токеном JWE (A256GCM) и общим ключом."""

from fastapi import APIRouter, Header

from app.schemas import TokenResponse
from app.security import decrypt_jwe_token, extract_bearer

router = APIRouter(tags=["private"])


@router.get(
    "/private/encrypted",
    response_model=TokenResponse,
    summary="Приватный, шифрованный JWE (A256GCM)",
)
def private_encrypted(authorization: str | None = Header(default=None)) -> TokenResponse:
    """Расшифровывает JWE общим ключом. Клиент встраивает такой же ключ."""
    token = extract_bearer(authorization)
    claims = decrypt_jwe_token(token)
    return TokenResponse(
        ok=True,
        endpoint="/private/encrypted",
        claims=claims,
        note="JWE расшифрован ключом, общим с клиентом. Расшифруйте, измените, зашифруйте.",
    )
