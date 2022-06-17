# VersionInfo helper script for PyInstaller

This repository contains helper scripts to dynamically create VersionInfo objects that can be embedded in .exe files created by PyInstaller.

This project was created because existing solutions to embed version information inside executables relied on creating artifact files that get read (and eval-ed) by PyInstaller during the build process.
Dynamically creating such files essentially boiled down to inserting data in a string template, with no guides to the user if their entered data is valid or not.
A bit of exploration of PyInstaller's source code and official Microsoft documentation revealed that it should be possible to
provide PyInstaller with necessary data straight from .spec files without file-read-and-eval step.
This approach has the added bonus of being type hint compatible, offering rich auto-complete in supported IDEs.

## Installation

`pip install versioninfo_helper`

## Usage

See [example_simple.onefile.spec](example_simple.onefile.spec) and [example_dynamic.onefile.spec](example_dynamic.onefile.spec) for examples on how to integrate VersionInfo creation directly into PyInstaller .spec files.
