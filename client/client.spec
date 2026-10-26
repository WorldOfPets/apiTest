# Spec-файл PyInstaller для учебного клиента (кросс-платформенный).
# Сборка: pyinstaller client/client.spec --noconfirm
#
# Результат по платформам:
#   Windows -> client/dist/ApiClient.exe
#   Linux   -> client/dist/ApiClient
#   macOS   -> client/dist/ApiClient и client/dist/ApiClient.app

import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['jwt', 'jwcrypto', 'jwcrypto.jwe', 'jwcrypto.jwk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ApiClient',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# На macOS дополнительно собираем .app-бандл, чтобы клиент запускался двойным кликом.
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='ApiClient.app',
        icon=None,
        bundle_identifier='com.training.apiclient',
        info_plist={
            'NSHighResolutionCapable': True,
            'LSBackgroundOnly': False,
        },
    )
