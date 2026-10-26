#!/usr/bin/env bash
# Запуск учебного API на http://0.0.0.0:8000 (macOS / Linux).
set -euo pipefail

# Переходим в корень репозитория (на уровень выше папки scripts).
cd "$(dirname "$0")/.."

# Активируем виртуальное окружение, если оно есть.
if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
else
    echo "Виртуальное окружение .venv не найдено."
    echo "Создайте его: python3 -m venv .venv && .venv/bin/pip install -r server/requirements.txt"
    exit 1
fi

exec python server/run.py
