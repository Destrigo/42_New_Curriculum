# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pac-man.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.'), ('README.md', '.')],
    hiddenimports=['pygame', 'mazegenerator', 'mazegenerator.mazegenerator'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pacman-42',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pacman-42',
)
