# -*- mode: python ; coding: utf-8 -*-
import os
import re
import subprocess

# Read version dynamically from version.py
with open('version.py') as _f:
    _content = _f.read()
_match = re.search(r"__version__ = ['\"]([^'\"]+)['\"]", _content)
APP_VERSION = _match.group(1)

# Find FFmpeg at build time (handles both Apple Silicon and Intel)
def _find_ffmpeg():
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True, check=True)
        path = result.stdout.strip()
        if path and os.path.exists(path):
            return path
    except subprocess.CalledProcessError:
        pass
    for p in ['/opt/homebrew/bin/ffmpeg', '/usr/local/bin/ffmpeg', '/usr/bin/ffmpeg']:
        if os.path.exists(p):
            return p
    raise RuntimeError("FFmpeg not found. Install with: brew install ffmpeg")

FFMPEG_PATH = _find_ffmpeg()

# Shared hiddenimports for both CLI and GUI
COMMON_HIDDEN = ['resources_rc', 'packaging', 'packaging.version']

common_analysis = {
    'pathex': [],
    'binaries': [],
    'datas': [
        ('medusa_core.py', '.'),
        ('version.py', '.'),
        ('styles', 'styles'),
        ('tools/version_manager.py', 'tools'),
        (FFMPEG_PATH, 'Resources'),
        ('FFMPEG_ATTRIBUTION.txt', 'Resources'),
    ],
    'hiddenimports': COMMON_HIDDEN,
    'excludes': ['tkinter', 'PyQt5', 'PyQt6'],
    'hookspath': [],
    'hooksconfig': {},
    'runtime_hooks': [],
    'win_no_prefer_redirects': False,
    'win_private_assemblies': False,
    'cipher': None,
    'noarchive': False,
}

# CLI version
cli_a = Analysis(
    ['medusa_cli.py'],
    **common_analysis
)

cli_pyz = PYZ(cli_a.pure, cli_a.zipped_data, cipher=None)

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
    argv_emulation=False,
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

# GUI version — merge common hidden imports with GUI-specific ones
gui_a = Analysis(
    ['medusa_gui.py'],
    **{
        **common_analysis,
        'hiddenimports': COMMON_HIDDEN + [
            'PySide6',
            'PySide6.QtCore',
            'PySide6.QtWidgets',
            'PySide6.QtGui',
            'shiboken6',
            'numpy',
            'numpy.core',
        ]
    }
)

gui_pyz = PYZ(gui_a.pure, gui_a.zipped_data, cipher=None)

gui_exe = EXE(
    gui_pyz,
    gui_a.scripts,
    [],
    exclude_binaries=True,
    name='Medusa_Wavetable_Utility',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file='entitlements.plist',
)

gui_coll = COLLECT(
    gui_exe,
    gui_a.binaries,
    gui_a.zipfiles,
    gui_a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Medusa_Wavetable_Utility',
)

app = BUNDLE(
    gui_coll,
    name='Medusa Wavetable Utility.app',
    icon='icon.icns',
    bundle_identifier='com.code404.medusa',
    info_plist={
        'CFBundleDisplayName': 'Medusa Wavetable Utility',
        'CFBundleName': 'Medusa Wavetable Utility',
        'CFBundleShortVersionString': APP_VERSION,
        'CFBundleVersion': APP_VERSION,
        'NSHighResolutionCapable': 'True',
        'LSBackgroundOnly': 'False',
        'NSHumanReadableCopyright': f'© 2025 Justin Maxwell',
    }
)
