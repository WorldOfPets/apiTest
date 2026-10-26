"""Тонкая HTTP-обёртка над учебным API.

Перед упаковкой клиента измените ``BASE_URL`` на текущий URL cloudpub
(либо сделайте его константой времени сборки).
"""

from typing import Any

import requests

from tokens import (
    build_encrypted_token,
    build_signed_token,
    build_unsigned_token,
)

# Укажите здесь текущий URL туннеля cloudpub перед сборкой exe.
# Оставляйте обычный http://, чтобы Wireshark видел токен в открытом виде.
BASE_URL = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 10


def _request(path: str, token: str | None = None) -> dict[str, Any]:
    """Выполняет GET-запрос и приводит ответ к формату, удобному для UI."""
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        return {
            "url": url,
            "request_headers": headers,
            "status": None,
            "error": str(exc),
        }

    try:
        body: Any = response.json()
    except ValueError:
        body = response.text

    return {
        "url": url,
        "request_headers": headers,
        "status": response.status_code,
        "headers": dict(response.headers),
        "body": body,
        "error": None,
    }


def call_public() -> dict[str, Any]:
    """GET /public — токен не требуется."""
    return _request("/public")


def call_private_none(role: str = "user") -> dict[str, Any]:
    """GET /private/none с неподписанным токеном."""
    return _request("/private/none", build_unsigned_token(role))


def call_private_admin(role: str = "admin") -> dict[str, Any]:
    """GET /private/admin с неподписанным токеном и выбранной ролью."""
    return _request("/private/admin", build_unsigned_token(role))


def call_private_signed(role: str = "user") -> dict[str, Any]:
    """GET /private/signed с токеном HS256."""
    return _request("/private/signed", build_signed_token(role))


def call_private_encrypted(role: str = "user") -> dict[str, Any]:
    """GET /private/encrypted с токеном JWE."""
    return _request("/private/encrypted", build_encrypted_token(role))
