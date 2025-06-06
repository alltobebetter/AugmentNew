# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主程序
a = Analysis(
    ['gui_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('favicon.ico', '.'),
        ('version.txt', '.'),
        ('favicon.ico', 'gui'),  # 也复制到gui目录
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'urllib3',
        'certifi',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'webbrowser',
        'threading',
        'json',
        'sqlite3',
        'glob',
        'zipfile',
        'shutil',
        'time',
        'os',
        'sys',
        'pathlib',
        're',
        'stat',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 收集文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AugmentNew',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 设置图标
    icon='favicon.ico',
    # 设置版本信息
    version='version_info.txt',
    # 请求管理员权限
    uac_admin=True,
    uac_uiaccess=False,
)

# 如果需要创建目录分发版本，取消注释以下代码
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='AugmentNew'
# )
