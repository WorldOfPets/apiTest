# Учебный API + клиент

Намеренно уязвимый сервис на FastAPI и скомпилированный клиент на PyQt6 для обучения
атакам на JWT. Студенты перехватывают трафик клиента в Wireshark и подделывают токены
для пяти эндпоинтов.

Полный план — в [`plans/plan.md`](plans/plan.md), исходные требования — в [`TODO.md`](TODO.md).

## Структура

- [`server/`](server/) — приложение FastAPI с пятью эндпоинтами
- [`client/`](client/) — клиент на PyQt6, собирается в `ApiClient.exe`
- [`tests/`](tests/) — набор тестов pytest для всех сценариев авторизации
- [`scripts/`](scripts/) — запуск, сборка, туннель, проверка утечки, брутфорс HS256 и хелперы JWE
- [`docs/`](docs/) — методичка студенту, руководство преподавателю, решения

## Эндпоинты

| Эндпоинт | Аутентификация |
|----------|----------------|
| `GET /public` | нет |
| `GET /private/none` | неподписанный JWT (`alg=none`) |
| `GET /private/admin` | неподписанный JWT, `role=admin` |
| `GET /private/signed` | HS256 со слабым встроенным секретом |
| `GET /private/encrypted` | JWE `A256GCM` с общим ключом |

## Быстрый старт

### Windows (cmd / PowerShell)

```
python -m venv .venv
.venv\Scripts\pip install -r server\requirements.txt -r client\requirements.txt pytest httpx
scripts\run_server.bat
```

### macOS / Linux

```
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt -r client/requirements.txt pytest httpx
bash scripts/run_server.sh
```

Затем откройте http://127.0.0.1:8000/docs для интерактивного просмотра API.

## Тесты

```
.venv\Scripts\python -m pytest tests -q
```

## Сборка и проверка клиента

Windows:

```
scripts\build_client.bat
.venv\Scripts\python scripts\verify_leak.py client\dist\ApiClient.exe
```

macOS / Linux:

```
bash scripts/build_client.sh
.venv/bin/python scripts/verify_leak.py client/dist/ApiClient
```

Результат сборки по платформам:
- Windows -> `client/dist/ApiClient.exe`
- Linux -> `client/dist/ApiClient`
- macOS -> `client/dist/ApiClient` и `client/dist/ApiClient.app`

Скрипт проверки должен вывести `secret123` и общий ключ JWE, подтверждая, что утечка
в собранном бинарнике присутствует.

## Предупреждение

Код намеренно небезопасен и предназначен только для обучения. Никогда не разворачивайте
его с реальными учётными данными или данными.
