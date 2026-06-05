# goose_detective.spec
# -*- mode: python ; coding: utf-8 -*-
import os
block_cipher = None

# Icon is optional — only use it if present, so the build doesn't fail without it.
_icon_path = os.path.join('assets', 'icons', 'goose.ico')
ICON = _icon_path if os.path.exists(_icon_path) else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/styles.qss', 'ui'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'pyannote.audio',
        'faster_whisper',
        'sounddevice',
        'soundfile',
        'openai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GooseDetective',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=ICON,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GooseDetective',
)
