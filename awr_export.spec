# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for AWR Export Tool."""

import os
import glob

block_cipher = None

project_dir = os.path.abspath('.')
venv_sp = os.path.join(project_dir, 'venv', 'Lib', 'site-packages')
pywin32_dlls = os.path.join(venv_sp, 'pywin32_system32')

# Collect pywin32 DLLs
binaries = []
for dll in glob.glob(os.path.join(pywin32_dlls, '*.dll')):
    binaries.append((dll, '.'))

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=binaries,
    datas=[],
    hiddenimports=[
        'win32com',
        'win32com.client',
        'win32com.client.dynamic',
        'win32com.client.gencache',
        'win32com.server',
        'win32api',
        'win32con',
        'pythoncom',
        'pywintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Not needed — trim build size
        'matplotlib',
        'matplotlib.tests',
        'numpy.tests',
        'tkinter.test',
        'pytest',
        'IPython',
        'notebook',
        'sphinx',
    ],
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
    name='awr_export',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='awr_export',
)
