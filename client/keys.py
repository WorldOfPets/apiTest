"""Секреты, встроенные в поставляемый клиент.

ВНИМАНИЕ: Намеренно небезопасно. Эти значения и есть суть упражнения — студенты
извлекают их из ``ApiClient.exe`` и используют для подделки/расшифровки токенов.
Обфускацию специально оставляем минимальной.
"""

import base64

# Должен совпадать с server/app/config.py:SECRET_KEY
JWT_HS256_SECRET = "secret123"

# Должен совпадать с server/app/config.py:JWE_PASSPHRASE (ровно 32 байта).
# Форма base64url ниже вычисляется так же, как на сервере, что гарантирует
# синхронность значений.
JWE_PASSPHRASE = "0123456789ABCDEF0123456789abcdef"
JWE_KEY_B64 = base64.urlsafe_b64encode(JWE_PASSPHRASE.encode("utf-8")).decode("utf-8")

JWE_ALG = "dir"
JWE_ENC = "A256GCM"
