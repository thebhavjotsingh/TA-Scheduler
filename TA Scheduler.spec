# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Collect all data files for ortools (CP-SAT solver)
datas, binaries, hiddenimports = collect_all('ortools')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas + [
        ('icon.icns', '.'), 
        ('icon.ico', '.'),
        ('src/config/styles.css', 'src/config/'),  # Include CSS stylesheet
    ],
    hiddenimports=hiddenimports + [
        'PySide6.QtCore',
        'PySide6.QtWidgets', 
        'PySide6.QtGui',
        'pandas',
        'ortools.sat.python.cp_model',
        'src.config.constants',
        'src.config.styles',
        'src.config.stylesheet_loader',
        'src.core.data_parser',
        'src.core.scheduler',
        'src.gui.main_window',
        'src.gui.widgets',
        'src.utils.time_utils',
    ],
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
    name='TA Scheduler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression for better icon quality
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns',  # Use .icns for macOS
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX compression for better quality
    upx_exclude=[],
    name='TA Scheduler',
)
app = BUNDLE(
    coll,
    name='TA Scheduler.app',
    icon='icon.icns',
    bundle_identifier=None,
)
