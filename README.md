# VersionInfo helper script for PyInstaller

This repository contains helper scripts to dynamically create VersionInfo objects that can be embedded in .exe files created by PyInstaller.

## Project Status

| Category | Workflow information |
|----------|--------------------- |
| [Published on PyPI]((https://pypi.org/project/versioninfo-helper/)) | [![PyPI - Version](https://img.shields.io/pypi/v/versioninfo_helper)](https://pypi.org/project/versioninfo-helper/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/versioninfo_helper)](https://pypi.org/project/versioninfo-helper/) [![📦 Publish Python Package](https://github.com/ReggX/versioninfo_helper/actions/workflows/publish.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/publish.yml) |
| [Documentation](https://reggx.github.io/versioninfo_helper/) | [![Documentation on Github Pages](https://img.shields.io/website?url=https%3A%2F%2Freggx.github.io%2Fversioninfo_helper%2F&label=Documentation%20on%20Github%20Pages)](https://reggx.github.io/versioninfo_helper/) [![📚 Build and publish documentation](https://github.com/ReggX/versioninfo_helper/actions/workflows/docs.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/docs.yml) |
| [Tests](https://coveralls.io/github/ReggX/versioninfo_helper?branch=main) | [![Coverage Status](https://coveralls.io/repos/github/ReggX/versioninfo_helper/badge.svg?branch=main)](https://coveralls.io/github/ReggX/versioninfo_helper?branch=main) [![🔄 Integration Testing](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_integration_tests.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_integration_tests.yml) [![🧪 Unittests with Coverage](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_unittests_coverage.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_unittests_coverage.yml) |
| Type annotations: inline | [![🔍 Typecheck: Mypy](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_typecheck_mypy.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_typecheck_mypy.yml) [![🧠 Typecheck: Pyright](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_typecheck_pyright.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_typecheck_pyright.yml) [![🦋 Typecheck: Pyrefly](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_typecheck_pyrefly.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_typecheck_pyrefly.yml) |
| Additional CI/CD workflows | [![🧹 Linters](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_lint.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_lint.yml) [![🚦 Noxfile Self Check](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_self_check.yml/badge.svg)](https://github.com/ReggX/versioninfo_helper/actions/workflows/nox_self_check.yml) |

## Motivation

This project was created because existing solutions to embed version information inside executables relied on creating artifact files that get read (and eval-ed) by PyInstaller during the build process. \
Dynamically creating such files essentially boiled down to inserting data in a string template, with no guides to the user if their entered data is valid or not. \
A bit of exploration of PyInstaller's source code and official Microsoft documentation revealed that it should be possible to provide PyInstaller with necessary data straight from .spec files without file-read-and-eval step. \
This approach has the added bonus of being type hint compatible, offering rich auto-complete in supported IDEs.

## Installation

Wheels are available on [PyPI](https://pypi.org/project/versioninfo-helper/), install with:

`pip install versioninfo_helper`

## Usage

See [example_simple.onefile.spec](https://github.com/ReggX/versioninfo_helper/blob/main/example_simple.onefile.spec) and [example_dynamic.onefile.spec](https://github.com/ReggX/versioninfo_helper/blob/main/example_dynamic.onefile.spec) for examples on how to integrate VersionInfo creation directly into PyInstaller .spec files.

Snippet of .spec file with embedded VersionInfo generation:
```python
...  # Skipped other parts of .spec file

def gen_version_info():  #  -> VSVersionInfo
    '''
    Helper function, which can be embedded in .spec file,
    generates VSVersionInfo instance for executable.
    '''
    from versioninfo_helper import CharsetCode
    from versioninfo_helper import LanguageID
    from versioninfo_helper import create_VersionInfo
    # version must be a tuple of 4 (16-bit) integers
    # hardcoded in this example, but can be generated dynamically as needed
    version = (1, 2, 3, 4)
    version_str = '.'.join(str(v) for v in version)

    return create_VersionInfo(
        version,
        strings=[
            {
                # all fields are described in included TypedDicts, 
                # so IDEs should offer auto-complete and type checks
                "lang_id": LanguageID.US_English,
                "charset_id": CharsetCode.Unicode,
                "fields": {
                    "CompanyName": 'Your Company Name LLC',
                    'FileDescription': f'AppName ({version_str})',
                    'FileVersion': f'{version_str}',
                    'InternalName': 'AppName.exe',
                    'LegalCopyright': '© 2026 Your Company Name LLC',
                    'OriginalFilename': 'AppName.exe',
                    'ProductName': 'AppName - Part of Product',
                    'ProductVersion': f'{version_str}',
                }
            }
        ]
    )

...  # Skipped other parts of .spec file

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
    version=gen_version_info()  # call your helper function here
)
```
