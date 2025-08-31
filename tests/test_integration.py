import json
import subprocess
from pathlib import Path
from typing import Any

import PyInstaller.__main__


# ------------------------------------------------------------------------------


def compile_extract_compare(
    tmp_path: Path,
    spec_file: Path,
    appname: str,
    expected_data: dict[str, Any],
) -> None:
    build_dir: Path = tmp_path / "build"
    dist_dir: Path = tmp_path / "dist"

    # Compile the exe
    PyInstaller.__main__.run(
        [
            str(spec_file.absolute()),
            "--workpath",
            str(build_dir.absolute()),
            "--distpath",
            str(dist_dir.absolute()),
        ]
    )

    # Check if the exe was created
    exe_file: Path = dist_dir / appname / f"{appname}.exe"
    assert exe_file.exists(), "Executable file was not created"

    # Use powershell to extract the version info as json
    subprocess.run(
        [
            "powershell",
            "-Command",
            f"(Get-ChildItem .\\{appname}.exe).VersionInfo "
            + "| ConvertTo-Json -Compress  "
            + "| Out-File -FilePath versioninfo.json -Encoding utf8",
        ],
        cwd=exe_file.parent,
        check=True,
    )

    # Check if the versioninfo.json file was created
    json_file = exe_file.parent / "versioninfo.json"
    assert json_file.exists(), "Version info JSON file was not created"

    # Read the json data
    with open(json_file, "r", encoding="utf-8-sig") as f:
        json_data = json.load(f)
    assert json_data is not None, "Version info JSON file is empty"

    assert json_data.keys() == expected_data.keys(), (
        "JSON data keys do not match expected keys"
    )

    def compare_keys(
        expected_data: dict, json_data: dict, parent: str = ""
    ) -> None:
        """Compare the keys and values of two dictionaries, including nested dictionaries."""
        for key in expected_data.keys():
            if isinstance(expected_data[key], dict):
                assert isinstance(json_data[key], dict), (
                    f"Key '{key}' ({parent}/{key}) is not a dictionary in JSON data"
                )
                compare_keys(
                    expected_data[key], json_data[key], parent=f"{parent}/{key}"
                )
            else:
                assert expected_data[key] == json_data[key], (
                    f"Value for key '{key}' ({parent}/{key}) does not match expected value\n"
                    f"Expected: {expected_data[key]}\n"
                    f"Got:   {json_data[key]}"
                )

    compare_keys(expected_data, json_data)


# ------------------------------------------------------------------------------


def test_no_metadata(tmp_path: Path) -> None:
    spec_file: Path = Path(__file__).parent / "no_metadata.spec"
    appname: str = "helloworld"
    exe_file: Path = tmp_path / "dist" / appname / f"{appname}.exe"
    expected_data: dict[str, Any] = {
        "Comments": None,
        "CompanyName": None,
        "FileBuildPart": 0,
        "FileDescription": None,
        "FileMajorPart": 0,
        "FileMinorPart": 0,
        "FileName": str(exe_file.absolute()),
        "FilePrivatePart": 0,
        "FileVersion": None,
        "InternalName": None,
        "IsDebug": False,
        "IsPatched": False,
        "IsPrivateBuild": False,
        "IsPreRelease": False,
        "IsSpecialBuild": False,
        "Language": None,
        "LegalCopyright": None,
        "LegalTrademarks": None,
        "OriginalFilename": None,
        "PrivateBuild": None,
        "ProductBuildPart": 0,
        "ProductMajorPart": 0,
        "ProductMinorPart": 0,
        "ProductName": None,
        "ProductPrivatePart": 0,
        "ProductVersion": None,
        "SpecialBuild": None,
        "FileVersionRaw": {
            "Major": 0,
            "Minor": 0,
            "Build": 0,
            "Revision": 0,
            "MajorRevision": 0,
            "MinorRevision": 0,
        },
        "ProductVersionRaw": {
            "Major": 0,
            "Minor": 0,
            "Build": 0,
            "Revision": 0,
            "MajorRevision": 0,
            "MinorRevision": 0,
        },
    }

    compile_extract_compare(tmp_path, spec_file, appname, expected_data)


# ------------------------------------------------------------------------------


def test_full_metadata(tmp_path: Path) -> None:
    spec_file: Path = Path(__file__).parent / "full_metadata.spec"
    appname: str = "helloworld"
    exe_file: Path = tmp_path / "dist" / appname / f"{appname}.exe"
    expected_data: dict[str, Any] = {
        "Comments": "Comments",
        "CompanyName": "CompanyName",
        "FileBuildPart": 3,
        "FileDescription": "FileDescription",
        "FileMajorPart": 1,
        "FileMinorPart": 2,
        "FileName": str(exe_file.absolute()),
        "FilePrivatePart": 4,
        "FileVersion": "FileVersion",
        "InternalName": "InternalName",
        "IsDebug": True,
        "IsPatched": True,
        "IsPrivateBuild": True,
        "IsPreRelease": True,
        "IsSpecialBuild": True,
        "Language": "English (United States)",
        "LegalCopyright": "LegalCopyright",
        "LegalTrademarks": "LegalTrademarks",
        "OriginalFilename": "OriginalFilename",
        "PrivateBuild": "PrivateBuild",
        "ProductBuildPart": 7,
        "ProductMajorPart": 5,
        "ProductMinorPart": 6,
        "ProductName": "ProductName",
        "ProductPrivatePart": 8,
        "ProductVersion": "ProductVersion",
        "SpecialBuild": "SpecialBuild",
        "FileVersionRaw": {
            "Major": 1,
            "Minor": 2,
            "Build": 3,
            "Revision": 4,
            "MajorRevision": 0,
            "MinorRevision": 4,
        },
        "ProductVersionRaw": {
            "Major": 5,
            "Minor": 6,
            "Build": 7,
            "Revision": 8,
            "MajorRevision": 0,
            "MinorRevision": 8,
        },
    }

    compile_extract_compare(tmp_path, spec_file, appname, expected_data)


# ------------------------------------------------------------------------------
