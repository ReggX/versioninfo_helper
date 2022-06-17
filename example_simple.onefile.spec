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
    # 3rd party imports
    from PyInstaller.archive import pyz_crypto as pyi_crypto  # noqa: F401
    from PyInstaller.building.api import COLLECT  # noqa: F401
    from PyInstaller.building.api import EXE  # noqa: F401
    from PyInstaller.building.api import MERGE  # noqa: F401
    from PyInstaller.building.api import PYZ  # noqa: F401
    from PyInstaller.building.build_main import Analysis  # noqa: F401
    from PyInstaller.building.datastruct import TOC  # noqa: F401
    from PyInstaller.building.datastruct import Tree  # noqa: F401
    from PyInstaller.building.osx import BUNDLE  # noqa: F401
    from PyInstaller.building.splash import Splash  # noqa: F401
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


block_cipher = None


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
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
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
