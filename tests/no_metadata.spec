# -*- mode: python ; coding: utf-8 -*-

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # These imports will get loaded into namespace by PyInstaller:
    from PyInstaller.building.api import COLLECT  # noqa: F401
    from PyInstaller.building.api import EXE  # noqa: F401
    from PyInstaller.building.api import MERGE  # noqa: F401
    from PyInstaller.building.api import PYZ  # noqa: F401
    from PyInstaller.building.build_main import Analysis  # noqa: F401
    from PyInstaller.building.datastruct import TOC  # noqa: F401
    from PyInstaller.building.datastruct import Tree  # noqa: F401
    from PyInstaller.building.splash import Splash  # noqa: F401

    # These globals will get loaded into namespace by PyInstaller:
    DISTPATH: str
    """
    The relative path to the dist folder where the application will be stored.
    The default path is relative to the current directory.
    If the --distpath option is used, DISTPATH contains that value.
    """
    HOMEPATH: str
    """
    The absolute path to the PyInstaller distribution, typically in the
    current Python site-packages folder.
    """
    SPEC: str
    """
    The complete spec file argument given to the pyinstaller command,
    for example myscript.spec or source/myscript.spec
    """
    specnm: str
    """
    The name of the spec file, for example myscript.
    """
    SPECPATH: str
    """
    The path prefix to the SPEC value as returned by os.path.split()
    """
    WARNFILE: str
    """
    The full path to the warnings file in the build directory,
    for example build/warn-myscript.txt
    """
    workpath: str
    """
    The path to the build directory. The default is relative to the current
    directory. If the workpath= option is used, workpath contains that value.
    """


a = Analysis(
    ['helloworld.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='helloworld',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='helloworld',
)
