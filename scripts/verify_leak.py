"""Проверяет, что встроенные секреты извлекаются из собранного exe.

Повторяет действия студента с ``pyinstxtractor``: распаковывает архив PyInstaller
и сканирует байткод клиента на наличие слабого секрета и общего ключа JWE.

Запуск: python scripts/verify_leak.py client/dist/ApiClient.exe
"""

import os
import sys
import tempfile
import types

from PyInstaller.archive.readers import CArchiveReader, ZlibArchiveReader

TARGETS = ("secret123", "0123456789ABCDEF0123456789abcdef")


def scan_code(code: types.CodeType, found: list[str]) -> None:
    for const in code.co_consts:
        if isinstance(const, str) and any(t in const for t in TARGETS):
            found.append(const)
        if isinstance(const, types.CodeType):
            scan_code(const, found)


def main(exe_path: str) -> int:
    reader = CArchiveReader(exe_path)
    pyz_name = next(n for n in reader.toc if n.endswith(".pyz"))
    pyz_path = os.path.join(tempfile.gettempdir(), "extracted_pyz.bin")
    with open(pyz_path, "wb") as handle:
        handle.write(reader.extract(pyz_name))

    archive = ZlibArchiveReader(pyz_path)
    found: list[str] = []
    for name in archive.toc:
        lowered = name.lower()
        if "keys" in lowered or "tokens" in lowered:
            scan_code(archive.extract(name), found)

    if found:
        print("ИЗВЛЕЧЁННЫЕ ИЗ EXE СЕКРЕТЫ:")
        for value in dict.fromkeys(found):
            print(f"  - {value}")
        return 0

    print("Секреты не найдены — возможно, клиент слишком обфусцирован.")
    return 1


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "client/dist/ApiClient.exe"
    raise SystemExit(main(target))
