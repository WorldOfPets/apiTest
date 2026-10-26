@echo off
REM Запуск учебного API на http://0.0.0.0:8000
cd /d "%~dp0.."
.venv\Scripts\python server\run.py
