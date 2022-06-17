'''
Helper Script to generate VSVersionInfo for PyInstaller.

Either use VSVersionInfo object created by create_VersionInfo(...) directly
in spec file or write to file with str(VSVersionInfo object) to get a
representation that PyInstaller can eval() and embed into your exe.
'''

from __future__ import annotations

# native imports
import sys
from collections.abc import Sequence
from datetime import datetime
from datetime import timezone
from enum import IntEnum
from enum import IntFlag

# 3rd party imports
from PyInstaller.utils.win32.versioninfo import FixedFileInfo
from PyInstaller.utils.win32.versioninfo import StringFileInfo
from PyInstaller.utils.win32.versioninfo import StringStruct
from PyInstaller.utils.win32.versioninfo import StringTable
from PyInstaller.utils.win32.versioninfo import VarFileInfo
from PyInstaller.utils.win32.versioninfo import VarStruct
from PyInstaller.utils.win32.versioninfo import VSVersionInfo


# Python 3.7 or higher
if sys.version_info < (3, 7):
    raise ImportError(
        "This module is strictly typed and can't be used in Python <3.7!"
    )

# Python 3.8 or higher
if sys.version_info >= (3, 8):
    # native imports
    from typing import Final
    from typing import TypedDict
else:
    # 3rd party imports
    from typing_extensions import Final
    from typing_extensions import TypedDict

# Python 3.9 or higher
if sys.version_info >= (3, 9):
    pass
else:
    pass

# Python 3.10 or higher
if sys.version_info >= (3, 10):
    # native imports
    from typing import TypeAlias
else:
    # 3rd party imports
    from typing_extensions import TypeAlias

# Python 3.11 or higher
if sys.version_info >= (3, 11):
    # native imports
    from typing import NotRequired
    from typing import Required
else:
    # 3rd party imports
    from typing_extensions import NotRequired
    from typing_extensions import Required


# ==============================================================================
# ===== FILETIME <--> datetime translation =====================================
# ==============================================================================

EPOCH_AS_FILETIME: Final = 116444736000000000  # January 1, 1970 as filetime
HUNDREDS_OF_NS: Final = 10000000


def datetime_to_filetime(dt: datetime) -> int:
    """
    Converts a datetime to a Windows filetime. If the object is
    time zone-naive, it is forced to UTC before conversion.
    """

    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = dt.replace(tzinfo=timezone.utc)

    filetime = EPOCH_AS_FILETIME + (int(dt.timestamp()) * HUNDREDS_OF_NS)
    return filetime + (dt.microsecond * 10)
# ------------------------------------------------------------------------------


def filetime_to_datetime(filetime: int) -> datetime:
    """
    Converts a Windows filetime number to a Python datetime. The new
    datetime object is timezone-aware with timezone UTC.
    """

    # Get seconds and remainder in terms of Unix epoch
    s, ns100 = divmod(filetime - EPOCH_AS_FILETIME, HUNDREDS_OF_NS)
    # Convert to datetime object, with remainder as microseconds.
    return (
        datetime.fromtimestamp(s, timezone.utc)
        .replace(microsecond=(ns100 // 10))
    )
# ------------------------------------------------------------------------------


def datetime_to_filetime_tuple(dt: datetime) -> tuple[int, int]:
    """
    Convert a datetime to a Windows filetime split into
    a tuple of two 32-bit integers.
    """

    filetime: int = datetime_to_filetime(dt)
    return (filetime >> 32, filetime & 0xFFFFFFFF)
# ------------------------------------------------------------------------------


# ==============================================================================
# ===== Constants used in Arguments ============================================
# ==============================================================================

# https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
# https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo


class FileFlags(IntFlag):
    '''
    Contains a bitmask that specifies the Boolean attributes of the file.
    This member can include one or more of the following values.

    https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
    https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
    '''

    VS_FF_None = 0x00000000  # not a real value in verrsrc.h
    '''
    Indicates that no FileFlags apply.
    Not a real value in verrsrc.h
    '''

    VS_FF_DEBUG = 0x00000001
    '''
    The file contains debugging information or is compiled with debugging
    features enabled.
    '''

    VS_FF_INFOINFERRED = 0x00000010
    '''
    The file's version structure was created dynamically;
    therefore, some of the members in this structure may be empty or incorrect.
    This flag should never be set in a file's VS_VERSIONINFO data.
    '''

    VS_FF_PATCHED = 0x00000004
    '''
    The file has been modified and is not identical to the original shipping
    file of the same version number.
    '''

    VS_FF_PRERELEASE = 0x00000002
    '''
    The file is a development version, not a commercially released product.
    '''

    VS_FF_PRIVATEBUILD = 0x00000008
    '''
    The file was not built using standard release procedures.
    If this flag is set, the StringFileInfo structure should contain a
    PrivateBuild entry.
    '''

    VS_FF_SPECIALBUILD = 0x00000020
    '''
    The file was built by the original company using standard release procedures
    but is a variation of the normal file of the same version number.
    If this flag is set, the StringFileInfo structure should contain a
    SpecialBuild entry.
    '''

    VS_FFI_FILEFLAGSMASK = 0x0000003F
    '''
    A combination (bitmask) of all valid Flags in FileFlags
    '''
# ------------------------------------------------------------------------------


class FileOS(IntFlag):
    '''
    The operating system for which this file was designed.
    This member can be one of the following values.

    An application can combine these values to indicate that the file was
    designed for one operating system running on another. It includes some of
    the most common ones like VOS_NT_WINDOWS32 out of the box.

    https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
    https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
    '''

    VOS_UNKNOWN = 0x00000000
    '''
    The operating system for which the file was designed is unknown.
    '''

    VOS_DOS = 0x00010000
    '''
    File was designed for MS-DOS.
    '''

    VOS_OS216 = 0x00020000
    '''
    The file was designed for 16-bit OS/2.
    '''

    VOS_OS232 = 0x00030000
    '''
    The file was designed for 32-bit OS/2.
    '''

    VOS_NT = 0x00040000
    '''
    File was designed for modern 32-bit Windows.
    '''

    VOS_WINCE = 0x00050000
    '''
    TODO: Add missing documentation
    '''

    VOS__BASE = 0x00000000
    '''
    TODO: Add missing documentation
    '''

    VOS__WINDOWS16 = 0x00000001
    '''
    File was designed for 16-bit Windows.
    '''

    VOS__PM16 = 0x00000002
    '''
    The file was designed for 16-bit Presentation Manager.
    '''

    VOS__PM32 = 0x00000003
    '''
    The file was designed for 32-bit Presentation Manager.
    '''

    VOS__WINDOWS32 = 0x00000004
    '''
    File was designed for 32-bit Windows.
    '''

    VOS_DOS_WINDOWS16 = 0x00010001
    '''
    File was designed for 16-bit Windows running with MS-DOS.
    '''

    VOS_DOS_WINDOWS32 = 0x00010004
    '''
    File was designed for 32-bit Windows running with MS-DOS.
    '''

    VOS_OS216_PM16 = 0x00020002
    '''
    The file was designed for 16-bit Presentation Manager running on
    16-bit OS/2.
    '''

    VOS_OS232_PM32 = 0x00030003
    '''
    The file was designed for 32-bit Presentation Manager running on
    32-bit OS/2.
    '''

    VOS_NT_WINDOWS32 = 0x00040004
    '''
    File was designed for modern 32-bit Windows.
    '''
# ------------------------------------------------------------------------------


class FileType(IntFlag):
    '''
    The general type of file.
    This member can be one of the following values.
    All other values are reserved.

    https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
    https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
    '''

    VFT_UNKNOWN = 0x00000000
    '''
    The file type is unknown to the system.
    '''

    VFT_APP = 0x00000001
    '''
    The file contains an application.
    '''

    VFT_DLL = 0x00000002
    '''
    The file contains a DLL.
    '''

    VFT_DRV = 0x00000003
    '''
    The file contains a device driver. If dwFileType is VFT_DRV,
    dwFileSubtype contains a more specific description of the driver.
    '''

    VFT_FONT = 0x00000004
    '''
    The file contains a font. If dwFileType is VFT_FONT,
    dwFileSubtype contains a more specific description of the font file.
    '''

    VFT_VXD = 0x00000005
    '''
    The file contains a virtual device.
    '''

    VFT_STATIC_LIB = 0x00000007
    '''
    The file contains a static-link library.
    '''
# ------------------------------------------------------------------------------


class FileSubtype(IntFlag):
    '''
    The function of the file.
    The possible values depend on the value of dwFileType.
    For all values of dwFileType not described in the following list,
    dwFileSubtype is zero.

    https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
    https://docs.microsoft.com/en-us/windows/win32/api/verrsrc/ns-verrsrc-vs_fixedfileinfo
    '''

    VFT2_UNKNOWN = 0x00000000
    '''
    The driver type is unknown by the system.
    '''

    VFT2_DRV_PRINTER = 0x00000001
    '''
    The file contains a printer driver.
    '''

    VFT2_DRV_KEYBOARD = 0x00000002
    '''
    The file contains a keyboard driver.
    '''

    VFT2_DRV_LANGUAGE = 0x00000003
    '''
    The file contains a language driver.
    '''

    VFT2_DRV_DISPLAY = 0x00000004
    '''
    The file contains a display driver.
    '''

    VFT2_DRV_MOUSE = 0x00000005
    '''
    The file contains a mouse driver.
    '''

    VFT2_DRV_NETWORK = 0x00000006
    '''
    The file contains a network driver.
    '''

    VFT2_DRV_SYSTEM = 0x00000007
    '''
    The file contains a system driver.
    '''

    VFT2_DRV_INSTALLABLE = 0x00000008
    '''
    The file contains an installable driver.
    '''

    VFT2_DRV_SOUND = 0x00000009
    '''
    The file contains a sound driver.
    '''

    VFT2_DRV_COMM = 0x0000000A
    '''
    The file contains a communications driver.
    '''

    VFT2_DRV_INPUTMETHOD = 0x0000000B
    '''
    TODO: Add missing documentation
    '''

    VFT2_DRV_VERSIONED_PRINTER = 0x0000000C
    '''
    The file contains a versioned printer driver.
    '''

    VFT2_FONT_RASTER = 0x00000001
    '''
    The file contains a raster font.
    '''

    VFT2_FONT_VECTOR = 0x00000002
    '''
    The file contains a vector font.
    '''

    VFT2_FONT_TRUETYPE = 0x00000003
    '''
    The file contains a TrueType font.
    '''
# ------------------------------------------------------------------------------


class LanguageID(IntEnum):
    '''
    Containts constants for the language IDs.

    For the long names, see the Remarks section of the following link:
    https://docs.microsoft.com/en-us/windows/win32/menurc/stringfileinfo-block

    Short tags (like en_us) are also supported but they require prefixing
    with `TAG__` (all caps, two underscores).
    See the following link for a list of short tags:
    https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid

    If your desired language is not included in this class, then you should
    still be able to use the raw integer value whereever this class is used.
    '''
    # Long names
    # https://docs.microsoft.com/en-us/windows/win32/menurc/stringfileinfo-block
    Arabic = 0x0401
    Bulgarian = 0x0402
    Catalan = 0x0403
    Traditional_Chinese = 0x0404
    Czech = 0x0405
    Danish = 0x0406
    German = 0x0407
    Greek = 0x0408
    US_English = 0x0409
    Castilian_Spanish = 0x040A
    Finnish = 0x040B
    French = 0x040C
    Hebrew = 0x040D
    Hungarian = 0x040E
    Icelandic = 0x040F
    Italian = 0x0410
    Japanese = 0x0411
    Korean = 0x0412
    Dutch = 0x0413
    Norwegian_Bokmal = 0x0414
    Swiss_Italian = 0x0810
    Belgian_Dutch = 0x0813
    Norwegian_Nynorsk = 0x0814
    Polish = 0x0415
    Portuguese_Brazil = 0x0416
    Rhaeto_Romanic = 0x0417
    Romanian = 0x0418
    Russian = 0x0419
    Croato_Serbian_Latin = 0x041A
    Slovak = 0x041B
    Albanian = 0x041C
    Swedish = 0x041D
    Thai = 0x041E
    Turkish = 0x041F
    Urdu = 0x0420
    Bahasa = 0x0421
    Simplified_Chinese = 0x0804
    Swiss_German = 0x0807
    UK_English = 0x0809
    Spanish_Mexico = 0x080A
    Belgian_French = 0x080C
    Canadian_French = 0x0C0C
    Swiss_French = 0x100C
    Portuguese_Portugal = 0x0816
    Serbo_Croatian_Cyrillic = 0x081A
    # Short tags, all starting with TAG__
    # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid
    # <=0x03FF: Short tags without culture identifier
    TAG__ar = 0x0001
    TAG__bg = 0x0002
    TAG__ca = 0x0003
    TAG__zh_Hans = 0x0004
    TAG__cs = 0x0005
    TAG__da = 0x0006
    TAG__de = 0x0007
    TAG__el = 0x0008
    TAG__en = 0x0009
    TAG__es = 0x000A
    TAG__fi = 0x000B
    TAG__fr = 0x000C
    TAG__he = 0x000D
    TAG__hu = 0x000E
    TAG__is = 0x000F
    TAG__it = 0x0010
    TAG__ja = 0x0011
    TAG__ko = 0x0012
    TAG__nl = 0x0013
    TAG__no = 0x0014
    TAG__pl = 0x0015
    TAG__pt = 0x0016
    TAG__rm = 0x0017
    TAG__ro = 0x0018
    TAG__ru = 0x0019
    TAG__hr = 0x001A
    TAG__sk = 0x001B
    TAG__sq = 0x001C
    TAG__sv = 0x001D
    TAG__th = 0x001E
    TAG__tr = 0x001F
    TAG__ur = 0x0020
    TAG__id = 0x0021
    TAG__uk = 0x0022
    TAG__be = 0x0023
    TAG__sl = 0x0024
    TAG__et = 0x0025
    TAG__lv = 0x0026
    TAG__lt = 0x0027
    TAG__tg = 0x0028
    TAG__fa = 0x0029
    TAG__vi = 0x002A
    TAG__hy = 0x002B
    TAG__az = 0x002C
    TAG__eu = 0x002D
    TAG__hsb = 0x002E
    TAG__mk = 0x002F
    TAG__st = 0x0030
    TAG__ts = 0x0031
    TAG__tn = 0x0032
    TAG__ve = 0x0033
    TAG__xh = 0x0034
    TAG__zu = 0x0035
    TAG__af = 0x0036
    TAG__ka = 0x0037
    TAG__fo = 0x0038
    TAG__hi = 0x0039
    TAG__mt = 0x003A
    TAG__se = 0x003B
    TAG__ga = 0x003C
    TAG__ms = 0x003E
    TAG__kk = 0x003F
    TAG__ky = 0x0040
    TAG__sw = 0x0041
    TAG__tk = 0x0042
    TAG__uz = 0x0043
    TAG__tt = 0x0044
    TAG__bn = 0x0045
    TAG__pa = 0x0046
    TAG__gu = 0x0047
    TAG__or = 0x0048
    TAG__ta = 0x0049
    TAG__te = 0x004A
    TAG__kn = 0x004B
    TAG__ml = 0x004C
    TAG__as = 0x004D
    TAG__mr = 0x004E
    TAG__sa = 0x004F
    TAG__mn = 0x0050
    TAG__bo = 0x0051
    TAG__cy = 0x0052
    TAG__km = 0x0053
    TAG__lo = 0x0054
    TAG__my = 0x0055
    TAG__gl = 0x0056
    TAG__kok = 0x0057
    TAG__sd = 0x0059
    TAG__syr = 0x005A
    TAG__si = 0x005B
    TAG__chr = 0x005C
    TAG__iu = 0x005D
    TAG__am = 0x005E
    TAG__tzm = 0x005F
    TAG__ks = 0x0060
    TAG__ne = 0x0061
    TAG__fy = 0x0062
    TAG__ps = 0x0063
    TAG__fil = 0x0064
    TAG__dv = 0x0065
    TAG__ff = 0x0067
    TAG__ha = 0x0068
    TAG__yo = 0x006A
    TAG__quz = 0x006B
    TAG__nso = 0x006C
    TAG__ba = 0x006D
    TAG__lb = 0x006E
    TAG__kl = 0x006F
    TAG__ig = 0x0070
    TAG__om = 0x0072
    TAG__ti = 0x0073
    TAG__gn = 0x0074
    TAG__haw = 0x0075
    TAG__ii = 0x0078
    TAG__arn = 0x007A
    TAG__moh = 0x007C
    TAG__br = 0x007E
    TAG__ug = 0x0080
    TAG__mi = 0x0081
    TAG__oc = 0x0082
    TAG__co = 0x0083
    TAG__gsw = 0x0084
    TAG__sah = 0x0085
    TAG__qut = 0x0086
    TAG__rw = 0x0087
    TAG__wo = 0x0088
    TAG__prs = 0x008C
    TAG__gd = 0x0091
    TAG__ku = 0x0092
    # >= 0x0400 Short tags with culture identifiers
    TAG__ar_SA = 0x0401
    TAG__bg_BG = 0x0402
    TAG__ca_ES = 0x0403
    TAG__zh_TW = 0x0404
    TAG__cs_CZ = 0x0405
    TAG__da_DK = 0x0406
    TAG__de_DE = 0x0407
    TAG__el_GR = 0x0408
    TAG__en_US = 0x0409
    TAG__es_ES_tradnl = 0x040A
    TAG__fi_FI = 0x040B
    TAG__fr_FR = 0x040C
    TAG__he_IL = 0x040D
    TAG__hu_HU = 0x040E
    TAG__is_IS = 0x040F
    TAG__it_IT = 0x0410
    TAG__ja_JP = 0x0411
    TAG__ko_KR = 0x0412
    TAG__nl_NL = 0x0413
    TAG__nb_NO = 0x0414
    TAG__pl_PL = 0x0415
    TAG__pt_BR = 0x0416
    TAG__rm_CH = 0x0417
    TAG__ro_RO = 0x0418
    TAG__ru_RU = 0x0419
    TAG__hr_HR = 0x041A
    TAG__sk_SK = 0x041B
    TAG__sq_AL = 0x041C
    TAG__sv_SE = 0x041D
    TAG__th_TH = 0x041E
    TAG__tr_TR = 0x041F
    TAG__ur_PK = 0x0420
    TAG__id_ID = 0x0421
    TAG__uk_UA = 0x0422
    TAG__be_BY = 0x0423
    TAG__sl_SI = 0x0424
    TAG__et_EE = 0x0425
    TAG__lv_LV = 0x0426
    TAG__lt_LT = 0x0427
    TAG__tg_Cyrl_TJ = 0x0428
    TAG__fa_IR = 0x0429
    TAG__vi_VN = 0x042A
    TAG__hy_AM = 0x042B
    TAG__az_Latn_AZ = 0x042C
    TAG__eu_ES = 0x042D
    TAG__hsb_DE = 0x042E
    TAG__mk_MK = 0x042F
    TAG__st_ZA = 0x0430
    TAG__ts_ZA = 0x0431
    TAG__tn_ZA = 0x0432
    TAG__ve_ZA = 0x0433
    TAG__xh_ZA = 0x0434
    TAG__zu_ZA = 0x0435
    TAG__af_ZA = 0x0436
    TAG__ka_GE = 0x0437
    TAG__fo_FO = 0x0438
    TAG__hi_IN = 0x0439
    TAG__mt_MT = 0x043A
    TAG__se_NO = 0x043B
    TAG__yi_001 = 0x043D
    TAG__ms_MY = 0x043E
    TAG__kk_KZ = 0x043F
    TAG__ky_KG = 0x0440
    TAG__sw_KE = 0x0441
    TAG__tk_TM = 0x0442
    TAG__uz_Latn_UZ = 0x0443
    TAG__tt_RU = 0x0444
    TAG__bn_IN = 0x0445
    TAG__pa_IN = 0x0446
    TAG__gu_IN = 0x0447
    TAG__or_IN = 0x0448
    TAG__ta_IN = 0x0449
    TAG__te_IN = 0x044A
    TAG__kn_IN = 0x044B
    TAG__ml_IN = 0x044C
    TAG__as_IN = 0x044D
    TAG__mr_IN = 0x044E
    TAG__sa_IN = 0x044F
    TAG__mn_MN = 0x0450
    TAG__bo_CN = 0x0451
    TAG__cy_GB = 0x0452
    TAG__km_KH = 0x0453
    TAG__lo_LA = 0x0454
    TAG__my_MM = 0x0455
    TAG__gl_ES = 0x0456
    TAG__kok_IN = 0x0457
    TAG__syr_SY = 0x045A
    TAG__si_LK = 0x045B
    TAG__chr_Cher_US = 0x045C
    TAG__iu_Cans_CA = 0x045D
    TAG__am_ET = 0x045E
    TAG__tzm_Arab_MA = 0x045F
    TAG__ks_Arab = 0x0460
    TAG__ne_NP = 0x0461
    TAG__fy_NL = 0x0462
    TAG__ps_AF = 0x0463
    TAG__fil_PH = 0x0464
    TAG__dv_MV = 0x0465
    TAG__ff_NG__ff_Latn_NG = 0x0467
    TAG__ha_Latn_NG = 0x0468
    TAG__yo_NG = 0x046A
    TAG__quz_BO = 0x046B
    TAG__nso_ZA = 0x046C
    TAG__ba_RU = 0x046D
    TAG__lb_LU = 0x046E
    TAG__kl_GL = 0x046F
    TAG__ig_NG = 0x0470
    TAG__kr_Latn_NG = 0x0471
    TAG__om_ET = 0x0472
    TAG__ti_ET = 0x0473
    TAG__gn_PY = 0x0474
    TAG__haw_US = 0x0475
    TAG__la_VA = 0x0476
    TAG__so_SO = 0x0477
    TAG__ii_CN = 0x0478
    TAG__arn_CL = 0x047A
    TAG__moh_CA = 0x047C
    TAG__br_FR = 0x047E
    TAG__ug_CN = 0x0480
    TAG__mi_NZ = 0x0481
    TAG__oc_FR = 0x0482
    TAG__co_FR = 0x0483
    TAG__gsw_FR = 0x0484
    TAG__sah_RU = 0x0485
    TAG__rw_RW = 0x0487
    TAG__wo_SN = 0x0488
    TAG__prs_AF = 0x048C
    TAG__gd_GB = 0x0491
    TAG__ku_Arab_IQ = 0x0492
    TAG__qps_ploc = 0x0501
    TAG__qps_ploca = 0x05FE
    TAG__ar_IQ = 0x0801
    TAG__ca_ES_valencia = 0x0803
    TAG__zh_CN = 0x0804
    TAG__de_CH = 0x0807
    TAG__en_GB = 0x0809
    TAG__es_MX = 0x080A
    TAG__fr_BE = 0x080C
    TAG__it_CH = 0x0810
    TAG__nl_BE = 0x0813
    TAG__nn_NO = 0x0814
    TAG__pt_PT = 0x0816
    TAG__ro_MD = 0x0818
    TAG__ru_MD = 0x0819
    TAG__sr_Latn_CS = 0x081A
    TAG__sv_FI = 0x081D
    TAG__ur_IN = 0x0820
    TAG__dsb_DE = 0x082E
    TAG__tn_BW = 0x0832
    TAG__se_SE = 0x083B
    TAG__ga_IE = 0x083C
    TAG__ms_BN = 0x083E
    TAG__bn_BD = 0x0845
    TAG__pa_Arab_PK = 0x0846
    TAG__ta_LK = 0x0849
    TAG__sd_Arab_PK = 0x0859
    TAG__iu_Latn_CA = 0x085D
    TAG__tzm_Latn_DZ = 0x085F
    TAG__ks_Deva_IN = 0x0860
    TAG__ne_IN = 0x0861
    TAG__ff_Latn_SN = 0x0867
    TAG__quz_EC = 0x086B
    TAG__ti_ER = 0x0873
    TAG__qps_plocm = 0x09FF
    TAG__ar_EG = 0x0C01
    TAG__zh_HK = 0x0C04
    TAG__de_AT = 0x0C07
    TAG__en_AU = 0x0C09
    TAG__es_ES = 0x0C0A
    TAG__fr_CA = 0x0C0C
    TAG__sr_Cyrl_CS = 0x0C1A
    TAG__se_FI = 0x0C3B
    TAG__mn_Mong_MN = 0x0C50
    TAG__dz_BT = 0x0C51
    TAG__quz_PE = 0x0C6B
    TAG__ar_LY = 0x1001
    TAG__zh_SG = 0x1004
    TAG__de_LU = 0x1007
    TAG__en_CA = 0x1009
    TAG__es_GT = 0x100A
    TAG__fr_CH = 0x100C
    TAG__hr_BA = 0x101A
    TAG__smj_NO = 0x103B
    TAG__tzm_Tfng_MA = 0x105F
    TAG__ar_DZ = 0x1401
    TAG__zh_MO = 0x1404
    TAG__de_LI = 0x1407
    TAG__en_NZ = 0x1409
    TAG__es_CR = 0x140A
    TAG__fr_LU = 0x140C
    TAG__bs_Latn_BA = 0x141A
    TAG__smj_SE = 0x143B
    TAG__ar_MA = 0x1801
    TAG__en_IE = 0x1809
    TAG__es_PA = 0x180A
    TAG__fr_MC = 0x180C
    TAG__sr_Latn_BA = 0x181A
    TAG__sma_NO = 0x183B
    TAG__ar_TN = 0x1C01
    TAG__en_ZA = 0x1C09
    TAG__es_DO = 0x1C0A
    TAG__fr_029 = 0x1C0C
    TAG__sr_Cyrl_BA = 0x1C1A
    TAG__sma_SE = 0x1C3B
    TAG__ar_OM = 0x2001
    TAG__en_JM = 0x2009
    TAG__es_VE = 0x200A
    TAG__fr_RE = 0x200C
    TAG__bs_Cyrl_BA = 0x201A
    TAG__sms_FI = 0x203B
    TAG__ar_YE = 0x2401
    TAG__es_CO = 0x240A
    TAG__fr_CD = 0x240C
    TAG__sr_Latn_RS = 0x241A
    TAG__smn_FI = 0x243B
    TAG__ar_SY = 0x2801
    TAG__en_BZ = 0x2809
    TAG__es_PE = 0x280A
    TAG__fr_SN = 0x280C
    TAG__sr_Cyrl_RS = 0x281A
    TAG__ar_JO = 0x2C01
    TAG__en_TT = 0x2C09
    TAG__es_AR = 0x2C0A
    TAG__fr_CM = 0x2C0C
    TAG__sr_Latn_ME = 0x2C1A
    TAG__ar_LB = 0x3001
    TAG__en_ZW = 0x3009
    TAG__es_EC = 0x300A
    TAG__fr_CI = 0x300C
    TAG__sr_Cyrl_ME = 0x301A
    TAG__ar_KW = 0x3401
    TAG__en_PH = 0x3409
    TAG__es_CL = 0x340A
    TAG__fr_ML = 0x340C
    TAG__ar_AE = 0x3801
    TAG__es_UY = 0x380A
    TAG__fr_MA = 0x380C
    TAG__ar_BH = 0x3C01
    TAG__en_HK = 0x3C09
    TAG__es_PY = 0x3C0A
    TAG__fr_HT = 0x3C0C
    TAG__ar_QA = 0x4001
    TAG__en_IN = 0x4009
    TAG__es_BO = 0x400A
    TAG__en_MY = 0x4409
    TAG__es_SV = 0x440A
    TAG__en_SG = 0x4809
    TAG__es_HN = 0x480A
    TAG__en_AE = 0x4C09
    TAG__es_NI = 0x4C0A
    TAG__es_PR = 0x500A
    TAG__es_US = 0x540A
    TAG__es_CU = 0x5C0A
    TAG__bs_Cyrl = 0x641A
    TAG__bs_Latn = 0x681A
    TAG__sr_Cyrl = 0x6C1A
    TAG__sr_Latn = 0x701A
    TAG__smn = 0x703B
    TAG__az_Cyrl = 0x742C
    TAG__sms = 0x743B
    TAG__zh = 0x7804
    TAG__nn = 0x7814
    TAG__bs = 0x781A
    TAG__az_Latn = 0x782C
    TAG__sma = 0x783B
    TAG__uz_Cyrl = 0x7843
    TAG__mn_Cyrl = 0x7850
    TAG__iu_Cans = 0x785D
    TAG__tzm_Tfng = 0x785F
    TAG__zh_Hant = 0x7C04
    TAG__nb = 0x7C14
    TAG__sr = 0x7C1A
    TAG__tg_Cyrl = 0x7C28
    TAG__dsb = 0x7C2E
    TAG__smj = 0x7C3B
    TAG__uz_Latn = 0x7C43
    TAG__pa_Arab = 0x7C46
    TAG__mn_Mong = 0x7C50
    TAG__sd_Arab = 0x7C59
    TAG__chr_Cher = 0x7C5C
    TAG__iu_Latn = 0x7C5D
    TAG__tzm_Latn = 0x7C5F
    TAG__ff_Latn = 0x7C67
    TAG__ha_Latn = 0x7C68
    TAG__ku_Arab = 0x7C92
# ------------------------------------------------------------------------------


class CharsetCode(IntEnum):
    '''
    Containts constants for the charset identifiers.

    See the Remarks section of the following link:
    https://docs.microsoft.com/en-us/windows/win32/menurc/stringfileinfo-block

    If your desired charset is not included in this class, then you should
    still be able to use the raw integer value whereever this class is used.
    '''
    ASCII = 0x0000
    Japan = 0x03A4
    Korea = 0x03B5
    Taiwan = 0x03B6
    Unicode = 0x04B0
    Latin_2 = 0x04E2
    Cyrillic = 0x04E3
    Multilingual = 0x04E4
    Greek = 0x04E5
    Turkish = 0x04E6
    Hebrew = 0x04E7
    Arabic = 0x04E8
# ------------------------------------------------------------------------------


# ==============================================================================
# ===== Type classes used in arguments of create_VersionInfo() =================
# ==============================================================================

class StringFileInfo_Dict(TypedDict, total=False):
    '''
    TypedDict with all recommended keys for StringFileInfo.
    Additional keys are allowed and will get embedded into VersionInfo.
    '''
    Comments: NotRequired[str]
    CompanyName: NotRequired[str]
    FileDescription: NotRequired[str]
    FileVersion: NotRequired[str]
    InternalName: NotRequired[str]
    LegalCopyright: NotRequired[str]
    LegalTrademarks: NotRequired[str]
    OriginalFilename: NotRequired[str]
    PrivateBuild: NotRequired[str]
    ProductName: NotRequired[str]
    ProductVersion: NotRequired[str]
    SpecialBuild: NotRequired[str]
# ------------------------------------------------------------------------------


class VersionInfo_Strings_Dict(TypedDict):
    '''
    TypedDict with all required keys for VersionInfo strings block.
    '''
    lang_id: Required[LanguageID | int]
    charset_id: Required[LanguageID | int]
    fields: Required[StringFileInfo_Dict]
# ------------------------------------------------------------------------------


VersionTuple: TypeAlias = 'tuple[int, int, int, int]'


# ==============================================================================
# ===== Functions ==============================================================
# ==============================================================================

def create_StringFileInfo_table(
    lang_id: LanguageID | int,
    charset_id: CharsetCode | int,
    *,
    Comments: str | None = None,
    CompanyName: str | None = None,
    FileDescription: str | None = None,
    FileVersion: str | None = None,
    InternalName: str | None = None,
    LegalCopyright: str | None = None,
    LegalTrademarks: str | None = None,
    OriginalFilename: str | None = None,
    PrivateBuild: str | None = None,
    ProductName: str | None = None,
    ProductVersion: str | None = None,
    SpecialBuild: str | None = None,
    **additional_strings: str,
) -> StringTable:
    '''
    Create a StringTable for the StringFileInfo block.
    '''
    # Table name
    name: str = f"{int(lang_id):04X}{int(charset_id):04X}"
    # Table entries
    kids: list[StringStruct] = []
    if Comments is not None:
        kids.append(StringStruct('Comments', Comments))
    if CompanyName is not None:
        kids.append(StringStruct('CompanyName', CompanyName))
    if FileDescription is not None:
        kids.append(StringStruct('FileDescription', FileDescription))
    if FileVersion is not None:
        kids.append(StringStruct('FileVersion', FileVersion))
    if InternalName is not None:
        kids.append(StringStruct('InternalName', InternalName))
    if LegalCopyright is not None:
        kids.append(StringStruct('LegalCopyright', LegalCopyright))
    if LegalTrademarks is not None:
        kids.append(StringStruct('LegalTrademarks', LegalTrademarks))
    if OriginalFilename is not None:
        kids.append(StringStruct('OriginalFilename', OriginalFilename))
    if PrivateBuild is not None:
        kids.append(StringStruct('PrivateBuild', PrivateBuild))
    if ProductName is not None:
        kids.append(StringStruct('ProductName', ProductName))
    if ProductVersion is not None:
        kids.append(StringStruct('ProductVersion', ProductVersion))
    if SpecialBuild is not None:
        kids.append(StringStruct('SpecialBuild', SpecialBuild))
    # We could have just used **fields and save ourselves a lot of similar code,
    # but then we wouldn't have the expected keyword arguments that are useful
    # when it comes to auto-completion.
    for key, value in additional_strings.items():
        kids.append(StringStruct(key, value))
    # create Table
    return StringTable(name, kids)
# ------------------------------------------------------------------------------


def create_VarStruct(
    lang_id: LanguageID | int,
    charset_id: CharsetCode | int,
    *additional_pairs: tuple[LanguageID | int, CharsetCode | int]
) -> VarStruct:
    '''
    Create VarStruct for the VarFileInfo block.
    '''
    # Table name
    name: str = "Translation"
    # Table entries
    # An array of one or more values that are language and code page
    # identifier pairs.
    # If you use the Var structure to list the languages your application or
    # DLL supports instead of using multiple version resources, use the Value
    # member to contain an array of DWORD values indicating the language and
    # code page combinations supported by this file. The low-order word of
    # each DWORD must contain a Microsoft language identifier, and the
    # high-order word must contain the IBM code page number. Either
    # high-order or low-order word can be zero, indicating that the file is
    # language or code page independent.
    kids: list[int] = [
        int(lang_id),
        int(charset_id),
    ]
    for lid, cid in additional_pairs:
        kids.extend([int(lid), int(cid)])
    return VarStruct(name, kids)
# ------------------------------------------------------------------------------


def create_VersionInfo(
    filevers: VersionTuple | None = None,
    prodvers: VersionTuple | None = None,
    mask: FileFlags | int | None = None,
    flags: FileFlags | int | None = None,
    OS: FileOS | int | None = None,
    fileType: FileType | int | None = None,
    subtype: FileSubtype | int | None = None,
    date: datetime | tuple[int, int] | None = None,
    strings: Sequence[VersionInfo_Strings_Dict] | None = None,
) -> VSVersionInfo:
    '''
    Create a VSVersionInfo instance with data provided in arguments.

    Arguments:

    ---

    - `filevers`

        A tuple of four 16-bit integers.
        For SemVer, use (MAJOR, MINOR, PATCH, 0).
        Default: `(0, 0, 0, 0)`

    ---

    - `prodvers`

        A tuple of four 16-bit integers
        Default: `filevers`

    ---

    - `mask`

        Contains a bitmask that specifies the valid bits in dwFileFlags
        (`flags`).
        A bit is valid only if it was defined when the file was created.
        Indicates which bits in the FILEFLAGS statement are valid.
        For 16-bit Windows, this value is 0x3f.
        (`FileFlags.VS_FFI_FILEFLAGSMASK`)
        Default: `FileFlags.VS_FFI_FILEFLAGSMASK` (0x3F)

    ---

    - `flags`

        Contains a bitmask that specifies the Boolean attributes of the file.
        This member can include one or more of the values defined in
        enum `FileFlags`.
        Default: `FileFlags.VS_FF_None` (0x00)

    ---

    - `OS`

        The operating system for which this file was designed.
        This member can be one of the values defined in enum `FileOS`.
        Default: `FileOS.VOS_NT_WINDOWS3` (0x00040004)

    ---

    - `fileType`

        The general type of file.
        This member can be one of the values defined in enum `FileType`.
        All other values are reserved by Microsoft.
        Default: `FileType.VFT_APP` (0x01)

    ---

    - `subtype`

        The function of the file.
        The possible values depend on the value of dwFileType (`fileType`).
        For all values of dwFileType other than `FileType.VFT_DRV` or
        `FileType.VFT_FONT`, dwFileSubtype is zero.
        Default: `FileSubtype.VFT2_UNKNOWN` (0x00)

    ---

    - `date`

        The file's creation date and time stamp.
        Accepts a datetime instance which will be translated into a Windows
        FILETIME struct or tuple `(high32, low32)` of two 32-bit integers
        representing the high and low part of the FILETIME struct.
        Default: `datetime.now(timezone.utc)` converted to FILETIME tuple

    ---

    - `strings`

        A sequence of dictionaries containing keys:

        + `lang_id`: LanguageCode | int

        + `charset_id`: CharsetCode | int

        + `fields`: {str: str} dict mapping StringStruct names to values, see
            `StringFileInfo_Dict`

    '''
    if filevers is None:
        filevers = (
            0,  # 16 bit uint, e.g. SemVer MAJOR
            0,  # 16 bit uint, e.g. SemVer MINOR
            0,  # 16 bit uint, e.g. SemVer PATCH
            0   # 16 bit uint, Optional, leave as 0 if unused
        )
    dwFileVersion_tuple: VersionTuple = filevers
    assert all(0 <= i < 2**16 for i in dwFileVersion_tuple)

    if prodvers is None:
        prodvers = filevers
    dwProductVersion_tuple: VersionTuple = prodvers
    assert all(0 <= i < 2**16 for i in dwProductVersion_tuple)

    if mask is None:
        mask = int(FileFlags.VS_FFI_FILEFLAGSMASK)
    dwFileFlagsMask: Final = mask

    if flags is None:
        flags = int(FileFlags.VS_FF_None)
    dwFileFlags: Final = flags

    if OS is None:
        OS = int(FileOS.VOS_NT_WINDOWS32)
    dwFileOS: Final = OS

    if fileType is None:
        fileType = int(FileType.VFT_APP)
    dwFileType: Final = fileType

    if subtype is None:
        subtype = int(FileSubtype.VFT2_UNKNOWN)
    dwFileSubtype: Final = subtype

    if date is None:
        date = datetime_to_filetime_tuple(datetime.now(timezone.utc))
    elif isinstance(date, datetime):
        date = datetime_to_filetime_tuple(date)
    dwFileDate: Final = date

    ffi: FixedFileInfo = FixedFileInfo(
        filevers=dwFileVersion_tuple,
        prodvers=dwProductVersion_tuple,
        mask=dwFileFlagsMask,
        flags=dwFileFlags,
        OS=dwFileOS,
        fileType=dwFileType,
        subtype=dwFileSubtype,
        date=dwFileDate,
    )

    kids: list[StringFileInfo | VarFileInfo] = []
    if strings is not None:
        string_infos: list[StringTable] = []
        var_infos: list[VarStruct] = []
        for info in strings:
            lang_id: int = int(info['lang_id'])
            charset_id: int = int(info['charset_id'])
            fields: StringFileInfo_Dict = info['fields']
            string_infos.append(create_StringFileInfo_table(
                lang_id=lang_id,
                charset_id=charset_id,
                **fields,
            ))
            var_infos.append(create_VarStruct(
                lang_id=lang_id,
                charset_id=charset_id,
            ))
        kids = [
            VarFileInfo(var_infos),
            StringFileInfo(string_infos),
        ]

    return VSVersionInfo(
        ffi=ffi,
        kids=kids,
    )
# ------------------------------------------------------------------------------
