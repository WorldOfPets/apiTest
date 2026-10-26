#!/usr/bin/env bash
# Пересборка клиента PyQt6 (macOS / Linux).
# Перед этим укажите в client/api.py актуальный URL туннеля (BASE_URL).
set -euo pipefail

cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
else
    echo "Виртуальное окружение .venv не найдено."
    echo "Создайте его: python3 -m venv .venv && .venv/bin/pip install -r client/requirements.txt"
    exit 1
fi

pyinstaller client/client.spec --noconfirm --distpath client/dist --workpath client/build

echo
echo "Готово. Артефакты в client/dist:"
ls -1 client/dist
