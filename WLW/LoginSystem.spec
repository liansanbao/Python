# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['LoginSystem.py', 'ShowWLW.py', 'Ui_WLW.py', 'StockBase/sqlite_db.py', 'StockBase/DailyLimitCrawl.py', 'StockBase/DateTimeUtils.py',
    'model/StockInfoModel.py', 'model/StockInfoCondition.py',
    'action/MainCapitalAction.py', 'action/MenuAction.py', 'action/StockInfoAction.py', 'action/WaringStockAction.py'],
    pathex=[],
    binaries=[],
    # 将资源文件和akshare模块的mini_racer.dll和calendar.json文件打包到编译目录
    # 将pyecharts相关库文件打包到编译目录(pyecharts\\datasets, pyecharts\\render\\templates)
    datas=[('_internal\\config', 'config'), ('_internal\\LOG', 'LOG'), ('_internal\\db', 'db'),
    ('_internal\\chart\\*', 'WLW\\action\\chart'), ('WebView\\bin\\*', 'WLW\\WebView\\bin'),
    ('_internal\\image\\*', 'image'), ('_internal\\akshare\\mini_racer.dll', '.'),
    ('_internal\\akshare\\file_fold\\calendar.json', 'akshare\\file_fold'),
    ('_internal\\font\\*', 'WLW'), ('_internal\\data\\*', 'fake_useragent\\data'),
    ('_internal\\pyecharts\\datasets\\*', 'pyecharts\\datasets'), ('_internal\\pyecharts\\render\\templates', 'pyecharts\\render\\templates')],
    hiddenimports=['PyQt6', 'pyecharts', 'StockBase', 'model', 'action'],#如果你的自定义模块依赖于其他未被自动检测到的模块，你可以在 hiddenimports 中添加它们：
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
    a.binaries,
    a.datas,
    [],
    exclude_binaries=True,
    name='WLW',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,# 如果需要控制台，改为True
    disable_windowed_traceback=True,
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
    name='WLW',
)