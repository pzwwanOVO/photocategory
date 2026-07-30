# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：单 exe，含模板/静态资源/离线地理编码数据。

构建：pyinstaller build.spec
输出：dist/小米图片分类整理.exe
"""
from PyInstaller.utils.hooks import collect_all, collect_data_files

datas = [
    ('templates', 'templates'),
    ('static', 'static'),
]
binaries = []
hiddenimports = [
    'win32com.client',
    'pythoncom',
    'win32timezone',
]

# 收集带数据/动态库的第三方依赖
for pkg in ['fast_geocn', 'shapely', 'pywebview', 'pythonnet',
            'clr_loader', 'exifread', 'PIL', 'pywin32',
            'simple_websocket', 'engineio', 'socketio',
            'flask_socketio', 'bidict', 'wsproto']:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception as e:
        print(f'collect_all({pkg}) 跳过：{e}')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'pandas',
              'pytest', 'IPython', 'jupyter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='小米图片分类整理',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,        # 窗口模式，无控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',       # 任务栏/EXE 图标
)
