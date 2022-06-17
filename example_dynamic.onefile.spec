'''
Example PyInstaller spec file for a onefile executable.
We are using the fact that spec files are just Python files to execute code
to dynamically generate the version info based on git tags.
'''

from __future__ import annotations

# native imports
from datetime import date
from datetime import datetime
from datetime import timezone
from hashlib import sha256
from pathlib import Path
from subprocess import CalledProcessError
from subprocess import check_output
from typing import TYPE_CHECKING
from typing import cast

# 3rd party imports
from versioninfo_helper import CharsetCode
from versioninfo_helper import FileFlags
from versioninfo_helper import LanguageID
from versioninfo_helper import StringFileInfo_Dict
from versioninfo_helper import VersionInfo_Strings_Dict
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


def get_version_from_git_tag() -> str:
    '''
    Use `git describe` to get current version information based on git tag.
    Intended to be used with tags like "v1.2.3".
    It uses --always --long to always include the commit hash and
    the current offset from last tag.
    '''
    git_path: Path = Path('.').parent

    try:
        git_tag: str = check_output(
            ['git', 'describe', '--always', '--long'],
            cwd=git_path
        ).strip().decode()
    except FileNotFoundError:
        print("[ERROR] Can't run git describe! Version info not updated!")
        raise
    except CalledProcessError:
        print("[ERROR] Invalid output from git describe!")
        raise

    return git_tag


def get_diff_index() -> str:
    '''
    Use `git diff-index` to check if there are uncomitted changes in the repo.
    '''
    git_path: Path = Path('.').parent

    try:
        git_diff_index: str = check_output(
            ['git', 'diff-index', 'HEAD', '--'],
            cwd=git_path
        ).strip().decode()
    except FileNotFoundError:
        print("[ERROR] Can't run git diff-index! Version info not updated!")
        raise
    except CalledProcessError:
        print("[ERROR] Invalid output from git describe!")
        raise
    return git_diff_index


def gen_version_info() -> VSVersionInfo:
    '''
    Generate VSVersionInfo instances for executable.
    '''
    git_tag = get_version_from_git_tag()
    diff_index: str = get_diff_index()
    build_date: str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    describe_split = git_tag.rsplit('-', maxsplit=2)
    tag = describe_split[0]
    commits = describe_split[1]
    short_hash = describe_split[2]
    build_flags: FileFlags = FileFlags.VS_FF_None
    full_diff_hash: str = ''
    if diff_index:
        full_diff_hash = sha256(
            diff_index.encode(),
            usedforsecurity=False
        ).hexdigest()
        diff_index = (
            f" *{full_diff_hash[-8:]}"
        )
        build_flags |= FileFlags.VS_FF_PRERELEASE | FileFlags.VS_FF_SPECIALBUILD
    ver_list: list[str | int] = tag[1:].split(".", maxsplit=3)  # type: ignore
    int_list: list[int] = [0, 0, 0, 0]
    for i in range(4):
        try:
            int_list[i] = int(ver_list[i])
        except (IndexError, TypeError, ValueError):
            pass
    ver_tuple = tuple(int_list[:4])
    ver_tuple = cast(tuple[int, int, int, int], ver_tuple)
    extended_version: str = f'ver {tag} rev {short_hash}{diff_index}'
    year: str = str(date.today().year)

    sfi: StringFileInfo_Dict = {
        # official strings:
        "CompanyName": 'Your Company Name LLC',
        'FileDescription': f'AppName ({extended_version})',
        'FileVersion': f'{git_tag}',
        'InternalName': 'AppName.exe',
        'LegalCopyright': f'© {year} Your Company Name LLC',
        'OriginalFilename': 'AppName.exe',
        'ProductName': 'AppName - Part of Product',
        'ProductVersion': f'{git_tag}',
        # unofficial strings, won't show up in file explorer:
        'GitTag': f'{tag}',
        'GitCommitOffset': f'{commits}',
        'GitShortHash': f'{short_hash}',
        'BuildDateUTCReadable': f'{build_date}',
    }  # pyright: ignore
    if build_flags & FileFlags.VS_FF_SPECIALBUILD:
        sfi.update({
            'SpecialBuild': f'Untracked changes: {full_diff_hash}',
        })

    strings: list[VersionInfo_Strings_Dict] = [
        {
            "lang_id": LanguageID.US_English,
            "charset_id": CharsetCode.Unicode,
            "fields": sfi.copy()  # copy in case you want to localize info
        },
        # supports multiple languages, but only one is strictly required
        {
            "lang_id": LanguageID.UK_English,
            "charset_id": CharsetCode.Unicode,
            "fields": sfi.copy()  # copy in case you want to localize info
        }
    ]

    return create_VersionInfo(
        ver_tuple,
        flags=build_flags,
        strings=strings
    )


VersionInfo: VSVersionInfo = gen_version_info()


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
    version=VersionInfo
)
