# /// script
# dependencies = ["nox"]
# ///


import nox


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
nox.options.default_venv_backend = VENV_BACKEND


# LINTERS ----------------------------------------------------------------------


@nox.session(reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND)
def flake8(session: nox.Session) -> None:
    session.install("-U", "flake8")
    session.run("python", "-m", "flake8", "./src")


@nox.session(reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND)
def ruff_check(session: nox.Session) -> None:
    session.install("-U", "ruff")
    session.run("ruff", "check", "./src")


# FORMAT CHECKS ----------------------------------------------------------------


@nox.session(default=False, reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND)
def black_check(session: nox.Session) -> None:
    session.install("-U", "black")
    session.run("black", "--check", "./src")


@nox.session(reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND)
def ruff_format_check(session: nox.Session) -> None:
    session.install("-U", "ruff")
    session.run("ruff", "format", "--check", "./src")


# FORMATTERS -------------------------------------------------------------------


@nox.session(default=False, reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND)
def black(session: nox.Session) -> None:
    session.install("-U", "black")
    session.run("black", "./src")


@nox.session(default=False, reuse_venv=REUSE_VENV, venv_backend=VENV_BACKEND)
def ruff_format(session: nox.Session) -> None:
    session.install("-U", "ruff")
    session.run("ruff", "format", "./src")


# TYPE CHECKERS ----------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_OLDEST_NEWEST,
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
    requires=["clean_old_coverage"],
)
def test_source(session: nox.Session) -> None:
    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        *nox.project.dependency_groups(pyproject, "test"),
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
)
def test_metadata(session: nox.Session) -> None:
    session.install("-U", "-e", ".", "pytest")
    session.run("pytest", "tests/test_metadata.py")


# BUILD DOCS -------------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
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
