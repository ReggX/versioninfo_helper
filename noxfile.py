# /// script
# dependencies = ["nox[uv]>=2025.5.1"]
# ///


import nox


nox.needs_version = ">=2025.5.1"


REUSE_VENV = False
VENV_BACKEND = "uv|virtualenv"
PYTHON_VERSION_MATRIX: list[str] = [
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
    "3.14",
]
PYTHON_OLDEST_NEWEST: list[str] = [
    PYTHON_VERSION_MATRIX[0],
    PYTHON_VERSION_MATRIX[-1],
]
PYINSTALLER_VERSION_MATRIX: list[str] = [
    "{%MIN_VERSION%}",
    "<6.0",
    "==6.0",
    "<7.0",
]
PYINSTALLER_MIN_VERSION: dict[str, str] = {
    "3.9": "==5.0",
    "3.10": "==5.0",
    "3.11": "==5.5",
    "3.12": "==5.13",
    "3.13": "==5.13",
    "3.14": "==5.13",
}
TYPING_EXTENSIONS_VERSION_MATRIX: list[str] = [
    "==4.13.2",
    "<5.0",
]
nox.options.default_venv_backend = VENV_BACKEND


# SELF CHECK -------------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["self_check"],
    requires=[
        "_self_check_Python_versions",
        "_self_check_new_PyInstaller",
        "_self_check_new_typing_extensions",
    ],
)
def self_check(session: nox.Session) -> None:
    session.notify("_self_check_Python_versions")
    session.notify("_self_check_new_PyInstaller")
    session.notify("_self_check_new_typing_extensions")


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    default=False,
    tags=["self_check"],
)
def _self_check_Python_versions(session: nox.Session) -> None:
    """
    Check if the PyInstaller minimum version lookup table needs to be updated.
    """
    if set(PYTHON_VERSION_MATRIX) != set(PYINSTALLER_MIN_VERSION.keys()):
        session.error(
            "PYTHON_VERSION_MATRIX and PYINSTALLER_MIN_VERSION keys must match"
        )


@nox.session(
    reuse_venv=False,
    venv_backend=VENV_BACKEND,
    default=False,
    tags=["self_check"],
)
def _self_check_new_PyInstaller(session: nox.Session) -> None:
    """
    Check if the PyInstaller version matrix needs to be updated.
    If a newer PyInstaller version is available than the latest in the matrix,
    the install will succeed and the session will fail.
    """
    next_version: str = PYINSTALLER_VERSION_MATRIX[-1].replace("<", ">=")
    session.install("-U", f"PyInstaller{next_version}", success_codes=[1])


@nox.session(
    reuse_venv=False,
    venv_backend=VENV_BACKEND,
    default=False,
    tags=["self_check"],
)
def _self_check_new_typing_extensions(session: nox.Session) -> None:
    """
    Check if the typing-extensions version matrix needs to be updated.
    If a newer typing-extensions version is available than the latest in the
    matrix, the install will succeed and the session will fail.
    """
    next_version: str = TYPING_EXTENSIONS_VERSION_MATRIX[-1].replace("<", ">=")
    session.install("-U", f"typing_extensions{next_version}", success_codes=[1])


# LINTERS ----------------------------------------------------------------------


@nox.session(reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND, tags=["lint"])
def flake8(session: nox.Session) -> None:
    session.install("-U", "flake8")
    session.run("python", "-m", "flake8", "./src")


@nox.session(reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND, tags=["lint"])
def ruff_check(session: nox.Session) -> None:
    session.install("-U", "ruff")
    session.run("ruff", "check", "./src")


# FORMAT CHECKS ----------------------------------------------------------------


@nox.session(
    default=False,
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["lint"],
)
def black_check(session: nox.Session) -> None:
    session.install("-U", "black")
    session.run("black", "--check", "./src")


@nox.session(reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND, tags=["lint"])
def ruff_format_check(session: nox.Session) -> None:
    session.install("-U", "ruff")
    session.run("ruff", "format", "--check", "./src")


# FORMATTERS -------------------------------------------------------------------


@nox.session(
    default=False,
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["format"],
)
def black(session: nox.Session) -> None:
    session.install("-U", "black")
    session.run("black", "./src")


@nox.session(
    default=False,
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["format"],
)
def ruff_format(session: nox.Session) -> None:
    session.install("-U", "ruff")
    session.run("ruff", "format", "./src")


# TYPE CHECKERS ----------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_OLDEST_NEWEST,
    tags=["typecheck"],
)
def mypy(session: nox.Session) -> None:
    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        "mypy",
        *nox.project.dependency_groups(pyproject, "types"),
    )
    session.run("mypy", "src", "--strict")


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_OLDEST_NEWEST,
    tags=["typecheck"],
)
def pyright(session: nox.Session) -> None:
    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        "pyright",
        *nox.project.dependency_groups(pyproject, "types"),
    )
    session.run("pyright", "src")


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_OLDEST_NEWEST,
    tags=["typecheck"],
)
def pyrefly(session: nox.Session) -> None:
    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        "pyrefly",
        *nox.project.dependency_groups(pyproject, "types"),
    )
    session.run("pyrefly", "check", "src")


# TEST SOURCE CODE -------------------------------------------------------------


@nox.session(
    venv_backend=None,
    default=False,
    tags=["coverage"],
)
def clean_old_coverage(session: nox.Session) -> None:
    import os
    import shutil

    if os.path.exists("htmlcov"):
        shutil.rmtree("htmlcov", ignore_errors=False)

    if os.path.exists(".coverage"):
        os.remove(".coverage")
    if os.path.exists("coverage.xml"):
        os.remove("coverage.xml")


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_VERSION_MATRIX,
    tags=["test", "coverage"],
    requires=["clean_old_coverage"],
)
@nox.parametrize("pyinstaller_version", PYINSTALLER_VERSION_MATRIX)
@nox.parametrize("typing_extensions_version", TYPING_EXTENSIONS_VERSION_MATRIX)
def test_source(
    session: nox.Session,
    pyinstaller_version: str,
    typing_extensions_version: str,
) -> None:
    if pyinstaller_version == "{%MIN_VERSION%}":
        assert isinstance(session.python, str)
        pyinstaller_version = PYINSTALLER_MIN_VERSION[session.python]

    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        *nox.project.dependency_groups(pyproject, "test"),
        f"PyInstaller{pyinstaller_version}",
        f"typing-extensions{typing_extensions_version}",
    )
    session.run(
        "pytest",
        "--cov",
        "--cov-append",
        "--cov-report",
        "xml",
        "--cov-report",
        "html",
        "--cov-report",
        "term-missing",
        "tests/test_source.py",
    )


# TEST GENERATED EXECUTABLE VERSIONINFO-----------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_VERSION_MATRIX,
    tags=["test"],
)
@nox.parametrize("pyinstaller_version", PYINSTALLER_VERSION_MATRIX)
def test_metadata(
    session: nox.Session,
    pyinstaller_version: str,
) -> None:
    if pyinstaller_version == "{%MIN_VERSION%}":
        assert isinstance(session.python, str)
        pyinstaller_version = PYINSTALLER_MIN_VERSION[session.python]

    session.install(
        "-U",
        "-e",
        ".",
        "pytest",
        f"PyInstaller{pyinstaller_version}",
    )
    session.run("pytest", "tests/test_metadata.py")


# BUILD DOCS -------------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["docs"],
)
def docs(session: nox.Session) -> None:
    session.install("-U", "-e", ".", "pdoc")
    session.run(
        "python",
        "-m",
        "pdoc",
        "versioninfo_helper",
        "-o",
        "./docs",
        "-t",
        "docs-theme",
    )


# RUN AS SCRIPT ----------------------------------------------------------------


if __name__ == "__main__":
    nox.main()
