import datetime as dt
import re
import sys

# ------------------------------------------------------------------------------


def test_datetime_to_filetime_known_value() -> None:
    from versioninfo_helper import datetime_to_filetime

    dt_ = dt.datetime(2020, 1, 1, 0, 0, 0, tzinfo=dt.timezone.utc)
    filetime: int = datetime_to_filetime(dt_)
    assert filetime == 132223104000000000


# ------------------------------------------------------------------------------


def test_datetime_to_filetime_naive() -> None:
    from versioninfo_helper import datetime_to_filetime

    dt_naive = dt.datetime(2020, 1, 1, 0, 0, 0)
    filetime_naive: int = datetime_to_filetime(dt_naive)
    assert isinstance(filetime_naive, int)
    assert filetime_naive == 132223104000000000


# ------------------------------------------------------------------------------


def test_datetime_to_filetime_different_timezone() -> None:
    from versioninfo_helper import datetime_to_filetime

    dt_tz = dt.datetime(
        2020,
        1,
        1,
        0,
        0,
        0,
        tzinfo=dt.timezone(dt.timedelta(hours=-5)),
    )
    filetime_tz: int = datetime_to_filetime(dt_tz)
    assert isinstance(filetime_tz, int)
    assert filetime_tz == 132223284000000000


# ------------------------------------------------------------------------------


def test_filetime_to_datetime_known_value() -> None:
    from versioninfo_helper import filetime_to_datetime

    filetime = 132223104000000000
    dt_: dt.datetime = filetime_to_datetime(filetime)
    assert dt_ == dt.datetime(2020, 1, 1, 0, 0, 0, tzinfo=dt.timezone.utc)


# ------------------------------------------------------------------------------


def test_filetime_to_datetime_round_trip() -> None:
    from versioninfo_helper import datetime_to_filetime, filetime_to_datetime

    original_dt = dt.datetime(2022, 5, 15, 12, 30, 45, tzinfo=dt.timezone.utc)
    filetime_rt: int = datetime_to_filetime(original_dt)
    dt_rt: dt.datetime = filetime_to_datetime(filetime_rt)
    assert dt_rt == original_dt


# ------------------------------------------------------------------------------


def test_filetime_to_datetime_different_timezone() -> None:
    from versioninfo_helper import datetime_to_filetime, filetime_to_datetime

    original_dt_tz = dt.datetime(
        2022,
        5,
        15,
        12,
        30,
        45,
        tzinfo=dt.timezone(dt.timedelta(hours=3)),
    )
    filetime_tz: int = datetime_to_filetime(original_dt_tz)
    dt_tz: dt.datetime = filetime_to_datetime(filetime_tz)
    assert dt_tz == original_dt_tz.astimezone(dt.timezone.utc)


# ------------------------------------------------------------------------------


def test_datetime_to_filetime_tuple_known_value() -> None:
    from versioninfo_helper import datetime_to_filetime_tuple

    dt_ = dt.datetime(2020, 1, 1, 0, 0, 0, tzinfo=dt.timezone.utc)
    filetime_tuple: tuple[int, int] = datetime_to_filetime_tuple(dt_)
    assert filetime_tuple == (30785590, 1761935360)


# ------------------------------------------------------------------------------


def test_datetime_to_filetime_tuple_naive() -> None:
    from versioninfo_helper import datetime_to_filetime_tuple

    dt_naive = dt.datetime(2020, 1, 1, 0, 0, 0)
    filetime_tuple_naive: tuple[int, int] = datetime_to_filetime_tuple(dt_naive)
    assert isinstance(filetime_tuple_naive, tuple)
    assert len(filetime_tuple_naive) == 2


# ------------------------------------------------------------------------------


def test_datetime_to_filetime_tuple_different_timezone() -> None:
    from versioninfo_helper import datetime_to_filetime_tuple

    dt_tz = dt.datetime(
        2020,
        1,
        1,
        0,
        0,
        0,
        tzinfo=dt.timezone(dt.timedelta(hours=-5)),
    )
    filetime_tuple_tz: tuple[int, int] = datetime_to_filetime_tuple(dt_tz)
    assert isinstance(filetime_tuple_tz, tuple)
    assert len(filetime_tuple_tz) == 2


# ------------------------------------------------------------------------------


def test_create_StringFileInfo_table_empty() -> None:
    from PyInstaller.utils.win32.versioninfo import StringTable

    from versioninfo_helper import (
        CharsetCode,
        LanguageID,
        create_StringFileInfo_table,
    )

    st: StringTable = create_StringFileInfo_table(
        LanguageID.US_English, CharsetCode.Unicode
    )
    assert isinstance(st, StringTable)
    expected = """StringTable(
  '040904B0',
  [])"""
    assert str(st) == expected


# ------------------------------------------------------------------------------


def test_create_StringFileInfo_table_with_fields() -> None:
    from PyInstaller.utils.win32.versioninfo import StringTable

    from versioninfo_helper import (
        CharsetCode,
        LanguageID,
        create_StringFileInfo_table,
    )

    st: StringTable = create_StringFileInfo_table(
        LanguageID.Greek,
        CharsetCode.ASCII,
        Comments="Comments",
        CompanyName="CompanyName",
        FileDescription="FileDescription",
        FileVersion="FileVersion",
        InternalName="InternalName",
        LegalCopyright="LegalCopyright",
        LegalTrademarks="LegalTrademarks",
        OriginalFilename="OriginalFilename",
        PrivateBuild="PrivateBuild",
        ProductName="ProductName",
        ProductVersion="ProductVersion",
        SpecialBuild="SpecialBuild",
        ExtraField="ExtraValue",
    )
    assert isinstance(st, StringTable)
    expected = """StringTable(
  '04080000',
  [StringStruct('Comments', 'Comments'),
  StringStruct('CompanyName', 'CompanyName'),
  StringStruct('FileDescription', 'FileDescription'),
  StringStruct('FileVersion', 'FileVersion'),
  StringStruct('InternalName', 'InternalName'),
  StringStruct('LegalCopyright', 'LegalCopyright'),
  StringStruct('LegalTrademarks', 'LegalTrademarks'),
  StringStruct('OriginalFilename', 'OriginalFilename'),
  StringStruct('PrivateBuild', 'PrivateBuild'),
  StringStruct('ProductName', 'ProductName'),
  StringStruct('ProductVersion', 'ProductVersion'),
  StringStruct('SpecialBuild', 'SpecialBuild'),
  StringStruct('ExtraField', 'ExtraValue')])"""
    assert str(st) == expected


# ------------------------------------------------------------------------------


def test_create_VarStruct_single_translation() -> None:
    from PyInstaller.utils.win32.versioninfo import VarStruct

    from versioninfo_helper import CharsetCode, LanguageID, create_VarStruct

    vs: VarStruct = create_VarStruct(LanguageID.US_English, CharsetCode.Unicode)
    assert isinstance(vs, VarStruct)
    expected = """VarStruct('Translation', [1033, 1200])"""
    assert str(vs) == expected


# ------------------------------------------------------------------------------


def test_create_VarStruct_multiple_translations() -> None:
    from PyInstaller.utils.win32.versioninfo import VarStruct

    from versioninfo_helper import CharsetCode, LanguageID, create_VarStruct

    vs: VarStruct = create_VarStruct(
        LanguageID.Greek,
        CharsetCode.ASCII,
        (LanguageID.Japanese, CharsetCode.Japan),
    )
    assert isinstance(vs, VarStruct)
    expected = """VarStruct('Translation', [1032, 0, 1041, 932])"""
    assert str(vs) == expected


# ------------------------------------------------------------------------------


def test_create_VersionInfo_empty() -> None:
    from PyInstaller.utils.win32.versioninfo import VSVersionInfo

    from versioninfo_helper import create_VersionInfo

    vi: VSVersionInfo = create_VersionInfo()
    assert isinstance(vi, VSVersionInfo)
    expected = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(0, 0, 0, 0),
    prodvers=(0, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[

  ]
)"""
    vi_str: str = re.sub(r"date=\(\d+, \d+\)", "date=(0, 0)", str(vi))
    assert vi_str == expected


# ------------------------------------------------------------------------------


def test_create_VersionInfo_with_date() -> None:
    from PyInstaller.utils.win32.versioninfo import VSVersionInfo

    from versioninfo_helper import create_VersionInfo

    vi: VSVersionInfo = create_VersionInfo(date=(30785590, 1761935360))
    assert isinstance(vi, VSVersionInfo)
    expected = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(0, 0, 0, 0),
    prodvers=(0, 0, 0, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(30785590, 1761935360)
    ),
  kids=[

  ]
)"""
    assert str(vi) == expected


# ------------------------------------------------------------------------------


def test_create_VersionInfo_with_full_details() -> None:
    from PyInstaller.utils.win32.versioninfo import VSVersionInfo

    from versioninfo_helper import (
        CharsetCode,
        FileFlags,
        FileOS,
        FileType,
        LanguageID,
        create_VersionInfo,
    )

    vi: VSVersionInfo = create_VersionInfo(
        (1, 2, 3, 4),
        (5, 6, 7, 8),
        mask=FileFlags.VS_FFI_FILEFLAGSMASK,
        flags=FileFlags.VS_FF_DEBUG | FileFlags.VS_FF_PRIVATEBUILD,
        OS=FileOS.VOS_NT_WINDOWS32,
        fileType=FileType.VFT_APP,
        subtype=0,
        date=dt.datetime(2020, 1, 1, 0, 0, 0, tzinfo=dt.timezone.utc),
        strings=[
            {
                "lang_id": LanguageID.US_English,
                "charset_id": CharsetCode.Unicode,
                "fields": {
                    "CompanyName": "Your Company Name LLC",
                    "FileDescription": "AppName (ver1.2.3.4)",
                    "FileVersion": "v1.2.3.4",
                    "InternalName": "AppName.exe",
                    "LegalCopyright": "© 2022 Your Company Name LLC",
                    "OriginalFilename": "AppName.exe",
                    "ProductName": "AppName - Part of Product",
                    "ProductVersion": "v1.2.3.4",
                },
            }
        ],
    )
    assert isinstance(vi, VSVersionInfo)
    expected = """# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 2, 3, 4),
    prodvers=(5, 6, 7, 8),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x9,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(30785590, 1761935360)
    ),
  kids=[
    VarFileInfo([VarStruct('Translation', [1033, 1200])]), 
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'Your Company Name LLC'),
        StringStruct('FileDescription', 'AppName (ver1.2.3.4)'),
        StringStruct('FileVersion', 'v1.2.3.4'),
        StringStruct('InternalName', 'AppName.exe'),
        StringStruct('LegalCopyright', '© 2022 Your Company Name LLC'),
        StringStruct('OriginalFilename', 'AppName.exe'),
        StringStruct('ProductName', 'AppName - Part of Product'),
        StringStruct('ProductVersion', 'v1.2.3.4')])
      ])
  ]
)"""
    assert str(vi) == expected


# ------------------------------------------------------------------------------


def test_create_VersionInfo_invalid_filevers() -> None:
    from pytest import raises

    from versioninfo_helper import create_VersionInfo

    with raises(ValueError):
        create_VersionInfo(filevers=(99999999999, 0, 0, 0))


# ------------------------------------------------------------------------------


def test_create_VersionInfo_invalid_prodvers() -> None:
    from pytest import raises

    from versioninfo_helper import create_VersionInfo

    with raises(ValueError):
        create_VersionInfo(prodvers=(99999999999, 0, 0, 0))


# ------------------------------------------------------------------------------


def test_deprecated_StringFileInfo_Dict() -> None:
    from versioninfo_helper import StringFileInfo_Dict, StringFileInfoDict

    assert hasattr(StringFileInfo_Dict, "__deprecated__")

    if sys.version_info >= (3, 14):
        from annotationlib import Format, get_annotations

        old_annotations: dict[str, str] = get_annotations(
            StringFileInfo_Dict, format=Format.STRING
        )
        new_annotations: dict[str, str] = get_annotations(
            StringFileInfoDict, format=Format.STRING
        )
    else:
        old_annotations = StringFileInfo_Dict.__annotations__
        new_annotations = StringFileInfoDict.__annotations__

    assert old_annotations == new_annotations


# ------------------------------------------------------------------------------


def test_deprecated_VersionInfo_Strings_Dict() -> None:
    from versioninfo_helper import (
        VersionInfo_Strings_Dict,
        VersionInfoStringsDict,
    )

    assert hasattr(VersionInfo_Strings_Dict, "__deprecated__")

    if sys.version_info >= (3, 14):
        from annotationlib import Format, get_annotations

        old_annotations: dict[str, str] = get_annotations(
            VersionInfo_Strings_Dict, format=Format.STRING
        )
        new_annotations: dict[str, str] = get_annotations(
            VersionInfoStringsDict, format=Format.STRING
        )
    else:
        old_annotations = VersionInfo_Strings_Dict.__annotations__
        new_annotations = VersionInfoStringsDict.__annotations__

    assert old_annotations == new_annotations


# ------------------------------------------------------------------------------
