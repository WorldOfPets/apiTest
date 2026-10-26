"""Интеграционные тесты эндпоинтов учебного API.

Запуск: pytest -q  (из корня репозитория)
Требуется установить зависимости сервера.
"""

import base64
import json
import sys
import time
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient
from jwcrypto import jwe, jwk

# Делаем ``server`` импортируемым независимо от текущей рабочей директории.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from app.config import JWE_KEY_B64, SECRET_KEY  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def unsigned_token(role: str = "user") -> str:
    header = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
    payload = b64url(
        json.dumps({"sub": "student", "role": role, "exp": int(time.time()) + 3600}).encode()
    )
    return f"{header}.{payload}."


def encrypted_token(role: str = "user") -> str:
    key = jwk.JWK(k=JWE_KEY_B64, kty="oct")
    env = jwe.JWE(
        json.dumps({"sub": "student", "role": role}).encode(),
        protected={"alg": "dir", "enc": "A256GCM"},
    )
    env.add_recipient(key)
    return env.serialize(compact=True)


# --------------------------------------------------------------------- public
def test_public_is_open():
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json()["ok"] is True


# ----------------------------------------------------------------------- none
def test_private_none_accepts_unsigned_token():
    response = client.get(
        "/private/none", headers={"Authorization": f"Bearer {unsigned_token()}"}
    )
    assert response.status_code == 200
    assert response.json()["claims"]["role"] == "user"


def test_private_none_requires_token():
    assert client.get("/private/none").status_code == 401


def test_private_none_accepts_tampered_signature():
    token = unsigned_token() + "totally-forged-signature"
    response = client.get(
        "/private/none", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------- admin
def test_admin_rejects_user_role():
    response = client.get(
        "/private/admin", headers={"Authorization": f"Bearer {unsigned_token('user')}"}
    )
    assert response.status_code == 403


def test_admin_accepts_forged_admin_role():
    response = client.get(
        "/private/admin", headers={"Authorization": f"Bearer {unsigned_token('admin')}"}
    )
    assert response.status_code == 200


# --------------------------------------------------------------------- signed
def test_signed_accepts_valid_token():
    token = jwt.encode({"sub": "student", "role": "user"}, SECRET_KEY, algorithm="HS256")
    response = client.get(
        "/private/signed", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_signed_rejects_bad_signature():
    token = jwt.encode({"sub": "x", "role": "user"}, "wrong-secret", algorithm="HS256")
    response = client.get(
        "/private/signed", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_signed_rejects_forged_admin_with_valid_weak_secret():
    # Студент восстанавливает SECRET_KEY и поэтому может подписать админский токен.
    token = jwt.encode({"sub": "x", "role": "admin"}, SECRET_KEY, algorithm="HS256")
    response = client.get(
        "/private/signed", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["claims"]["role"] == "admin"


# ------------------------------------------------------------------ encrypted
def test_encrypted_accepts_valid_token():
    response = client.get(
        "/private/encrypted", headers={"Authorization": f"Bearer {encrypted_token()}"}
    )
    assert response.status_code == 200
    assert response.json()["claims"]["role"] == "user"


def test_encrypted_accepts_forged_admin_with_shared_key():
    response = client.get(
        "/private/encrypted",
        headers={"Authorization": f"Bearer {encrypted_token('admin')}"},
    )
    assert response.status_code == 200
    assert response.json()["claims"]["role"] == "admin"


def test_encrypted_rejects_tampered_token():
    token = encrypted_token()
    tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
    response = client.get(
        "/private/encrypted", headers={"Authorization": f"Bearer {tampered}"}
    )
    assert response.status_code == 401
