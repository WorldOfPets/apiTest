@echo off
REM Пересборка клиента PyQt6 в client\dist\ApiClient.exe
REM Перед этим не забудьте указать в client\api.py актуальный URL туннеля (BASE_URL).
cd /d "%~dp0.."
.venv\Scripts\pyinstaller client\client.spec --noconfirm --distpath client\dist --workpath client\build
