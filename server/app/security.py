"""Хелперы работы с токенами для учебного API.

Все три схемы токенов проверяются намеренно небезопасным способом, чтобы студенты
могли отрабатывать подделку, взлом и изменение:

* ``decode_none_jwt``   -> доверяет неподписанному JWT ``alg=none``
* ``verify_hs256_jwt``  -> проверяет HS256 намеренно слабым секретом
* ``decrypt_jwe_token`` -> расшифровывает JWE общим симметричным ключом
"""

import base64
import json
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwcrypto import jwe, jwk

from app.config import JWE_KEY_B64, JWT_ALGORITHM, SECRET_KEY


def _b64url_decode(data: str) -> bytes:
    """Декодирует base64url, восстанавливая недостающий padding."""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def extract_bearer(authorization: str | None) -> str:
    """Извлекает сырой токен из заголовка ``Authorization: Bearer <token>``."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует заголовок Authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Заголовок Authorization должен быть вида 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return parts[1].strip()


def decode_none_jwt(token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Декодирует неподписанный JWT (``alg=none``) БЕЗ проверки подписи.

    Это и есть основная уязвимость: сегмент подписи полностью игнорируется,
    поэтому любой может собрать токен с произвольными claims.
    """
    parts = token.split(".")
    if len(parts) < 2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный JWT: ожидаются хотя бы сегменты заголовка и payload",
        )
    try:
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Некорректная кодировка JWT: {exc}",
        ) from exc
    return header, payload


def verify_hs256_jwt(token: str) -> dict[str, Any]:
    """Проверяет HS256 JWT слабым общим секретом."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истёк",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Недействительный токен: {exc}",
        ) from exc


def decrypt_jwe_token(token: str) -> dict[str, Any]:
    """Расшифровывает JWE compact-токен общим симметричным ключом."""
    key = jwk.JWK(k=JWE_KEY_B64, kty="oct")
    try:
        envelope = jwe.JWE()
        envelope.deserialize(token, key=key)
        payload = envelope.payload
    except Exception as exc:  # noqa: BLE001 - показать любую ошибку jwcrypto
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Не удалось расшифровать токен: {exc}",
        ) from exc
    try:
        return json.loads(payload)
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Расшифрованный payload не является корректным JSON: {exc}",
        ) from exc


def require_admin(payload: dict[str, Any]) -> None:
    """Бросает 403, если в декодированных claims нет ``role == 'admin'``."""
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется роль администратора",
        )
