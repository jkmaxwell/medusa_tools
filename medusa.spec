# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Common analysis settings
common_analysis = {
    'pathex': [],
    'binaries': [],
    'datas': [('medusa_core.py', '.')],
    'hiddenimports': ['numpy', 'numpy.core'],
    'hookspath': [],
    'hooksconfig': {},
    'runtime_hooks': [],
    'excludes': [],
    'win_no_prefer_redirects': False,
    'win_private_assemblies': False,
    'cipher': block_cipher,
    'noarchive': False,
}

# CLI version
cli_a = Analysis(
    ['medusa_mac.py'],
    **common_analysis
)

cli_pyz = PYZ(cli_a.pure, cli_a.zipped_data, cipher=block_cipher)

cli_exe = EXE(
    cli_pyz,
    cli_a.scripts,
    [],
    exclude_binaries=True,
    name='medusa_cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

cli_coll = COLLECT(
    cli_exe,
    cli_a.binaries,
    cli_a.zipfiles,
    cli_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='medusa_cli',
)

# GUI version
gui_a = Analysis(
    ['medusa_gui.py'],
    **{
        **common_analysis,
        'hiddenimports': common_analysis['hiddenimports'] + ['tkinter']
    }
)

gui_pyz = PYZ(gui_a.pure, gui_a.zipped_data, cipher=block_cipher)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    [],
    exclude_binaries=True,
    name='Medusa',
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

gui_coll = COLLECT(
    gui_exe,
    gui_a.binaries,
    gui_a.zipfiles,
    gui_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Medusa',
)

# Only create app bundle for GUI version
app = BUNDLE(
    gui_coll,
    name='Medusa.app',
    icon='icon.icns',
    bundle_identifier='com.code404.medusa',
    info_plist={
        'CFBundleDisplayName': 'Medusa Wavetable Tool',
        'CFBundleName': 'Medusa',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True'
    }
)