# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['medusa_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('medusa_wavetable_tool.py', '.'),
        ('medusa_wav_preprocessor.py', '.')
    ],
    hiddenimports=[],
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
    name='Medusa Wavetable Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Medusa Wavetable Tool',
)

app = BUNDLE(
    coll,
    name='Medusa Wavetable Tool.app',
    icon=None,
    bundle_identifier='com.code404.medusawavetabletool',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True'
    }
)