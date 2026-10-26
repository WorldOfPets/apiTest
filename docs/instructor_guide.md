# Руководство преподавателю

## Обзор

Проект содержит намеренно уязвимый учебный API и скомпилированный клиент на PyQt6.
Студенты перехватывают трафик клиента и подделывают токены. Каждый из пяти эндпоинтов
демонстрирует свою слабость аутентификации.

## Кроссплатформенность

Проект собирается и запускается на Windows, macOS и Linux.

- Сервер и клиент — чистый Python без платформо-зависимого кода.
- Скрипты запуска и сборки есть в двух вариантах:
  - Windows: `scripts\run_server.bat`, `scripts\build_client.bat`
  - macOS/Linux: `scripts/run_server.sh`, `scripts/build_client.sh`
- `client/client.spec` собирает exe на Windows, бинарник на Linux и дополнительно
  `.app`-бандл на macOS.
- Команды окружения и тестов:
  - создание окружения: `python -m venv .venv` (Windows) или `python3 -m venv .venv` (macOS/Linux)
  - тесты: `.venv\Scripts\python -m pytest tests -q` (Windows) или `.venv/bin/python -m pytest tests -q` (macOS/Linux)

Важно: сборку нужно выполнять на той же ОС, где клиент будет запускаться. PyInstaller не
делает кросс-компиляцию: exe для Windows собирается только на Windows, бинарник для Linux —
на Linux, приложение для macOS — на macOS.

## Порядок запуска

1. Запустите API.

   Windows:

   ```
   scripts\run_server.bat
   ```

   macOS / Linux:

   ```
   bash scripts/run_server.sh
   ```

2. Убедитесь, что он доступен локально:

   ```
   curl http://127.0.0.1:8000/public
   ```

3. Откройте его публично **по обычному HTTP** (обязательно, чтобы Wireshark видел токены):

   ```
   cloudpub http 8000
   ```

   Зафиксируйте публичный URL, который выведет cloudpub.

4. Пропишите этот URL в `client/api.py` (`BASE_URL`) и пересоберите.

   Windows:

   ```
   scripts\build_client.bat
   ```

   macOS / Linux:

   ```
   bash scripts/build_client.sh
   ```

5. Передайте студентам собранный клиент и сообщите им URL:
   - Windows: `client/dist/ApiClient.exe`
   - Linux: `client/dist/ApiClient`
   - macOS: `client/dist/ApiClient` и `client/dist/ApiClient.app`

## Критично: перехват должен быть в открытом виде

- Wireshark не расшифровывает TLS. Если клиент работает по HTTPS, студенты увидят только
  шифротекст.
- Предпочтительно открывать API по HTTP через туннель.
- Запасной вариант: пусть студенты запускают клиент против `http://127.0.0.1:8000` и
  перехватывают loopback-адаптер либо перехватывают на машине с сервером.
- На macOS/Linux loopback-перехват удобен через `lo0` (macOS) или `lo` (Linux) с фильтром
  `tcp port 8000`.

## Внедрённые уязвимости

| Эндпоинт | Слабость |
|----------|----------|
| `/private/none` | подпись не проверяется (`alg=none`) |
| `/private/admin` | неподписанный токен плюс доверие claim `role` |
| `/private/signed` | HS256 со слабым секретом, встроенным в клиент |
| `/private/encrypted` | ключ JWE общий с клиентом |

## Ожидаемые решения студентов

- Задачи 2–3: собранный вручную токен `alg=none` с `role=admin`.
- Задача 4: восстановить `secret123` (подбором из токена или из бинарника) и переподписать.
- Задача 5: восстановить общий ключ JWE и зашифровать заново.

Точные значения приведены в `docs/solutions.md`.

## Проверка утечки перед занятием

Windows:

```
.venv\Scripts\python scripts\verify_leak.py client\dist\ApiClient.exe
```

macOS / Linux:

```
.venv/bin/python scripts/verify_leak.py client/dist/ApiClient
```

Скрипт обязан вывести и `secret123`, и общий ключ JWE. Если нет — клиент упакован со
слишком сильной обфускацией, ослабьте её.

## Типичные ошибки

- Студенты запускают Wireshark, но перехватывают не тот интерфейс (Wi-Fi вместо loopback).
- exe собран под устаревший URL туннеля после перезапусков — пересоберите клиент.
- HTTP-прокси или QUIC/HTTP3 могут обходить ожидаемый путь перехвата.
- Студенты вставляют токен от `/private/encrypted` в jwt.io и видят `Invalid Compact JWS`.
  Это ожидаемо: это JWE (5 сегментов), а не JWS. Укажите им на `scripts/jwe_helper.py`.
- Токен в блоке «Сгенерированный токен» валиден только для эндпоинта, чья кнопка была
  нажата последней. Подписанные/JWE-токены используют схему нажатой кнопки.
- На macOS первый запуск собранного приложения может блокироваться Gatekeeper
  (неподписанный бандл). Обойдите это через правый клик > «Открыть» либо снимите
  карантин: `xattr -dr com.apple.quarantine client/dist/ApiClient.app`.
- На Linux собранному бинарнику может понадобиться бит выполнения: `chmod +x client/dist/ApiClient`.

## Безопасность

Этот API намеренно небезопасен. Никогда не разворачивайте его с реальными учётными данными
или данными и закрывайте туннель после занятия.
