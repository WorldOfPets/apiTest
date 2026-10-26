"""Сборщики токенов, которыми клиент обращается к учебному API.

Повторяют три схемы, которые принимает сервер:
* неподписанный JWT ``alg=none``
* JWT HS256, подписанный слабым встроенным секретом
* JWE (A256GCM), зашифрованный общим встроенным ключом
"""

import base64
import json
import time
from typing import Any

import jwt
from jwcrypto import jwe, jwk

from keys import JWE_ALG, JWE_ENC, JWE_KEY_B64, JWT_HS256_SECRET

DEFAULT_TTL_SECONDS = 3600


def _b64url_encode(data: bytes) -> str:
    """base64url-кодирование без padding, как требует JWT."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def default_claims(role: str = "user", subject: str = "student") -> dict[str, Any]:
    """Собирает стандартный набор claims, используемый во всех упражнениях."""
    now = int(time.time())
    return {
        "sub": subject,
        "role": role,
        "iat": now,
        "exp": now + DEFAULT_TTL_SECONDS,
    }


def build_unsigned_token(role: str = "user") -> str:
    """Возвращает неподписанный JWT ``alg=none``: ``header.payload.`` (точка в конце).

    Собирается вручную, потому что PyJWT отказывается выдавать токены ``alg=none``.
    """
    header = {"alg": "none", "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(
        json.dumps(default_claims(role), separators=(",", ":")).encode("utf-8")
    )
    return f"{header_b64}.{payload_b64}."


def build_signed_token(role: str = "user") -> str:
    """Возвращает JWT HS256, подписанный слабым встроенным секретом."""
    return jwt.encode(default_claims(role), JWT_HS256_SECRET, algorithm="HS256")


def build_encrypted_token(role: str = "user") -> str:
    """Возвращает JWE compact-токен (``dir`` + ``A256GCM``) с общим ключом."""
    plaintext = json.dumps(default_claims(role), separators=(",", ":")).encode("utf-8")
    key = jwk.JWK(k=JWE_KEY_B64, kty="oct")
    envelope = jwe.JWE(
        plaintext,
        protected={"alg": JWE_ALG, "enc": JWE_ENC},
    )
    envelope.add_recipient(key)
    return envelope.serialize(compact=True)


def decode_unsigned_payload(token: str) -> dict[str, Any]:
    """Декодирует payload неподписанного токена (без проверки)."""
    payload_b64 = token.split(".")[1]
    padding = "=" * (-len(payload_b64) % 4)
    return json.loads(base64.urlsafe_b64decode(payload_b64 + padding))
