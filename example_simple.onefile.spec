'''
Example PyInstaller spec file for a onefile executable.
'''

from __future__ import annotations

# native imports
from typing import TYPE_CHECKING

# 3rd party imports
from versioninfo_helper import CharsetCode
from versioninfo_helper import LanguageID
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


def gen_version_info() -> VSVersionInfo:
    '''
    Generate VSVersionInfo instances for executable.
    '''
    # version must be a tuple of 4 (16-bit) integers
    version = (1, 2, 3, 4)
    version_str = '.'.join(str(v) for v in version)

    return create_VersionInfo(
        version,
        strings=[
            {
                "lang_id": LanguageID.US_English,
                "charset_id": CharsetCode.Unicode,
                "fields": {
                    "CompanyName": 'Your Company Name LLC',
                    'FileDescription': f'AppName ({version_str})',
                    'FileVersion': f'{version_str}',
                    'InternalName': 'AppName.exe',
                    'LegalCopyright': '© 2022 Your Company Name LLC',
                    'OriginalFilename': 'AppName.exe',
                    'ProductName': 'AppName - Part of Product',
                    'ProductVersion': f'{version_str}',
                }
            }
        ]
    )


a = Analysis(
    ['appname.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AppName',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon='icon.ico',
    version=gen_version_info()
)
