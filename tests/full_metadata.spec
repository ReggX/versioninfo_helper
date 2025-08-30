# -*- mode: python ; coding: utf-8 -*-

import sys
from typing import TYPE_CHECKING

from PyInstaller.utils.win32.versioninfo import VSVersionInfo

from versioninfo_helper import CharsetCode
from versioninfo_helper import FileFlags
from versioninfo_helper import LanguageID
from versioninfo_helper import StringFileInfoDict
from versioninfo_helper import VersionInfoStringsDict
from versioninfo_helper import create_VersionInfo


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

    # This won't get loaded automatically, but we only need its type info:
    from PyInstaller.utils.win32.versioninfo import VSVersionInfo  # noqa: F401

file_ver_tuple = (1, 2, 3, 4)
product_ver_tuple = (5, 6, 7, 8)
build_flags: FileFlags = FileFlags.VS_FFI_FILEFLAGSMASK
sfi: StringFileInfoDict = {
    "Comments": "Comments",
    "CompanyName": "CompanyName",
    "FileDescription": "FileDescription",
    "FileVersion": "FileVersion",
    "InternalName": "InternalName",
    "LegalCopyright": "LegalCopyright",
    "LegalTrademarks": "LegalTrademarks",
    "OriginalFilename": "OriginalFilename",
    "PrivateBuild": "PrivateBuild",
    "ProductName": "ProductName",
    "ProductVersion": "ProductVersion",
    "SpecialBuild": "SpecialBuild",
}
strings: list[VersionInfoStringsDict] = [
    {
        "lang_id": LanguageID.US_English,
        "charset_id": CharsetCode.Unicode,
        "fields": sfi.copy(),  # copy in case you want to localize info
    }
]

vsinfo: VSVersionInfo = create_VersionInfo(
    file_ver_tuple, product_ver_tuple, flags=build_flags, strings=strings,
)


del sys.modules["versioninfo_helper"]


a = Analysis(
    ["helloworld.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name="helloworld",
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
    version=vsinfo,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="helloworld",
)
