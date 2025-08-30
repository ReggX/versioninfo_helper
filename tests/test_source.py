import re

import pytest
import versioninfo_helper
import datetime


def test_datetime_to_filetime() -> None:
    # Test known value: 2020-01-01 00:00:00 UTC
    dt = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    filetime = versioninfo_helper.datetime_to_filetime(dt)
    assert filetime == 132223104000000000

    # Test naive datetime (assumed to be in local timezone)
    dt_naive = datetime.datetime(2020, 1, 1, 0, 0, 0)
    filetime_naive = versioninfo_helper.datetime_to_filetime(dt_naive)
    assert isinstance(filetime_naive, int)

    # Test with different timezone
    dt_tz = datetime.datetime(
        2020,
        1,
        1,
        0,
        0,
        0,
        tzinfo=datetime.timezone(datetime.timedelta(hours=-5)),
    )
    filetime_tz = versioninfo_helper.datetime_to_filetime(dt_tz)
    assert isinstance(filetime_tz, int)
    assert filetime_tz != filetime


def test_filetime_to_datetime() -> None:
    # Test known value: 2020-01-01 00:00:00 UTC
    filetime = 132223104000000000
    dt = versioninfo_helper.filetime_to_datetime(filetime)
    assert dt == datetime.datetime(
        2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
    )

    # Test round-trip conversion
    original_dt = datetime.datetime(
        2022, 5, 15, 12, 30, 45, tzinfo=datetime.timezone.utc
    )
    filetime_rt = versioninfo_helper.datetime_to_filetime(original_dt)
    dt_rt = versioninfo_helper.filetime_to_datetime(filetime_rt)
    assert dt_rt == original_dt

    # Test with different timezone
    original_dt_tz = datetime.datetime(
        2022,
        5,
        15,
        12,
        30,
        45,
        tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
    )
    filetime_tz = versioninfo_helper.datetime_to_filetime(original_dt_tz)
    dt_tz = versioninfo_helper.filetime_to_datetime(filetime_tz)
    assert dt_tz == original_dt_tz.astimezone(datetime.timezone.utc)


def test_datetime_to_filetime_tuple() -> None:
    # Test known value: 2020-01-01 00:00:00 UTC
    dt = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    filetime_tuple = versioninfo_helper.datetime_to_filetime_tuple(dt)
    assert filetime_tuple == (30785590, 1761935360)  # Low and high parts

    # Test naive datetime (assumed to be in local timezone)
    dt_naive = datetime.datetime(2020, 1, 1, 0, 0, 0)
    filetime_tuple_naive = versioninfo_helper.datetime_to_filetime_tuple(
        dt_naive
    )
    assert isinstance(filetime_tuple_naive, tuple)
    assert len(filetime_tuple_naive) == 2

    # Test with different timezone
    dt_tz = datetime.datetime(
        2020,
        1,
        1,
        0,
        0,
        0,
        tzinfo=datetime.timezone(datetime.timedelta(hours=-5)),
    )
    filetime_tuple_tz = versioninfo_helper.datetime_to_filetime_tuple(dt_tz)
    assert isinstance(filetime_tuple_tz, tuple)
    assert len(filetime_tuple_tz) == 2
    assert filetime_tuple_tz != filetime_tuple


def test_create_StringFileInfo_table() -> None:
    from PyInstaller.utils.win32.versioninfo import StringTable

    st = versioninfo_helper.create_StringFileInfo_table(
        versioninfo_helper.LanguageID.US_English,
        versioninfo_helper.CharsetCode.Unicode,
    )
    assert isinstance(st, StringTable)
    expected = """StringTable(
  '040904B0',
  [])"""
    assert str(st) == expected

    st = versioninfo_helper.create_StringFileInfo_table(
        versioninfo_helper.LanguageID.Greek,
        versioninfo_helper.CharsetCode.ASCII,
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


def test_create_VarStruct() -> None:
    from PyInstaller.utils.win32.versioninfo import VarStruct

    vs = versioninfo_helper.create_VarStruct(
        versioninfo_helper.LanguageID.US_English,
        versioninfo_helper.CharsetCode.Unicode,
    )
    assert isinstance(vs, VarStruct)
    expected = """VarStruct('Translation', [1033, 1200])"""
    assert str(vs) == expected

    vs = versioninfo_helper.create_VarStruct(
        versioninfo_helper.LanguageID.Greek,
        versioninfo_helper.CharsetCode.ASCII,
        (
            versioninfo_helper.LanguageID.Japanese,
            versioninfo_helper.CharsetCode.Japan,
        ),
    )
    assert isinstance(vs, VarStruct)
    expected = """VarStruct('Translation', [1032, 0, 1041, 932])"""
    assert str(vs) == expected


def test_create_VersionInfo() -> None:
    from PyInstaller.utils.win32.versioninfo import VSVersionInfo

    vi = versioninfo_helper.create_VersionInfo()
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
    vi = re.sub(r"date=\(\d+, \d+\)", "date=(0, 0)", str(vi))
    assert str(vi) == expected

    vi = versioninfo_helper.create_VersionInfo(date=(30785590, 1761935360))
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

    vi = versioninfo_helper.create_VersionInfo(
        (1, 2, 3, 4),
        (5, 6, 7, 8),
        mask=versioninfo_helper.FileFlags.VS_FFI_FILEFLAGSMASK,
        flags=versioninfo_helper.FileFlags.VS_FF_DEBUG
        | versioninfo_helper.FileFlags.VS_FF_PRIVATEBUILD,
        OS=versioninfo_helper.FileOS.VOS_NT_WINDOWS32,
        fileType=versioninfo_helper.FileType.VFT_APP,
        subtype=0,
        date=datetime.datetime(
            2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
        ),
        strings=[
            {
                "lang_id": versioninfo_helper.LanguageID.US_English,
                "charset_id": versioninfo_helper.CharsetCode.Unicode,
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

    with pytest.raises(ValueError):
        versioninfo_helper.create_VersionInfo(filevers=(99999999999, 0, 0, 0))

    with pytest.raises(ValueError):
        versioninfo_helper.create_VersionInfo(prodvers=(99999999999, 0, 0, 0))
