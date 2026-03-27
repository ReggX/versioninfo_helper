# /// script
# dependencies = ["nox[uv]>=2025.5.1"]
# ///


from collections import namedtuple

import nox


nox.needs_version = ">=2025.5.1"

# NOX CONFIG -------------------------------------------------------------------
REUSE_VENV = False
VENV_BACKEND = "uv|virtualenv"
nox.options.default_venv_backend = VENV_BACKEND

# VERSION MATRICES -------------------------------------------------------------
PYTHON_VERSION_MATRIX: list[str] = [
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
    "3.14",
    "3.15",
]
PYINSTALLER_VERSION_MATRIX: list[str] = [
    # The goal of this matrix is to test test the lowest and highest possible
    # version of each major version of PyInstaller, to catch any
    # incompatibilities that may arise with new Python versions.
    # Since the minimum usable PyInstaller version for each Python version is
    # different, we have multiple minimum versions in the matrix, which are
    # skipped thanks to the AUTO_SKIPS list and the skip_combination helper
    # function.
    #
    # ----- 5.x
    "==5.0",  #  Minimum version for Python 3.9, 3.10
    "==5.5",  #  Minimum version for Python 3.11
    "==5.13",  # Minimum version for Python 3.12, 3.13, 3.14
    "<6.0",  #   Highest 5.x version
    #
    # ----- 6.x
    "==6.0",  #  Lowest 6.x version
    # Minimum version for Python 3.15 unknown
    # - Current status (2026-03-27): Latest (6.19) still incompatible
    "<7.0",  #   Highest 6.x version
    #
    # Once PyInstaller 7.0 is released, add "==7.0" and "<8.0" to the matrix,
    # and update the AUTO_SKIPS list accordingly.
]
TYPING_EXTENSIONS_VERSION_MATRIX: list[str] = [
    # ----- 4.x
    "==4.13.2",  # Lowest 4.x version
    "<5.0",  #     Highest 4.x version
]

VerCombi = namedtuple(
    "VerCombi",
    ["python", "pyinstaller", "typing_extensions"],
)
# Using the builtin `any` as an "any version matches" sentinel

AUTO_SKIPS: list[VerCombi] = [
    # ===== Below Minimum versions =====
    # Since we have different minimum PyInstaller versions for different
    # Python versions, we need to skip some combinations of Python and
    # PyInstaller versions that are known to be incompatible. The
    # typing-extensions version is not relevant for the incompatibility, so
    # we set it to any to indicate that it matches
    #
    # ===== Above Maximum versions =====
    # Currently unuused since all our dependencies support all vof our
    # supported Python versions
    #
    # ===== Cut for efficiency =====
    # In cases where we already test a lower and higher version in the same
    # major version, testing the middle versions is redundant and can be
    # skipped for efficiency.
    #
    #
    # ----- Python 3.9 -----
    # --- below minimum
    # none
    # --- cut for efficiency
    VerCombi(python="3.9", pyinstaller="==5.5", typing_extensions=any),
    VerCombi(python="3.9", pyinstaller="==5.13", typing_extensions=any),
    # --- above maximum
    # none
    #
    #
    # ----- Python 3.10 -----
    # --- below minimum
    # none
    # --- cut for efficiency
    VerCombi(python="3.10", pyinstaller="==5.5", typing_extensions=any),
    VerCombi(python="3.10", pyinstaller="==5.13", typing_extensions=any),
    # --- above maximum
    # none
    #
    #
    # ----- Python 3.11 -----
    # --- below minimum
    VerCombi(python="3.11", pyinstaller="==5.0", typing_extensions=any),
    # --- cut for efficiency
    VerCombi(python="3.11", pyinstaller="==5.13", typing_extensions=any),
    # --- above maximum
    # none
    #
    #
    # ----- Python 3.12 -----
    # --- below minimum
    VerCombi(python="3.12", pyinstaller="==5.0", typing_extensions=any),
    VerCombi(python="3.12", pyinstaller="==5.5", typing_extensions=any),
    # --- cut for efficiency
    # none
    # --- above maximum
    # none
    #
    #
    # ----- Python 3.13 -----
    # --- below minimum
    VerCombi(python="3.13", pyinstaller="==5.0", typing_extensions=any),
    VerCombi(python="3.13", pyinstaller="==5.5", typing_extensions=any),
    # --- cut for efficiency
    # none
    # --- above maximum
    # none
    #
    #
    # ----- Python 3.14 -----
    # --- below minimum
    VerCombi(python="3.14", pyinstaller="==5.0", typing_extensions=any),
    VerCombi(python="3.14", pyinstaller="==5.5", typing_extensions=any),
    # --- cut for efficiency
    # none
    # --- above maximum
    # none
    #
    #
    # ----- Python 3.15 -----
    # --- below minimum
    VerCombi(python="3.15", pyinstaller="==5.0", typing_extensions=any),
    VerCombi(python="3.15", pyinstaller="==5.5", typing_extensions=any),
    VerCombi(python="3.15", pyinstaller="==5.13", typing_extensions=any),
    VerCombi(python="3.15", pyinstaller="<6.0", typing_extensions=any),
    VerCombi(python="3.15", pyinstaller="==6.0", typing_extensions=any),
    # --- cut for efficiency
    # none
    # --- above maximum
    # none
]


# HELPER: SKIP NON INCOMPATIBLE COMNINATIONS -----------------------------------


def skip_combination(
    python_version: str | None = None,
    pyinstaller_version: str | None = None,
    typing_extensions_version: str | None = None,
) -> bool:
    """
    Skip the session if the combination of Python, PyInstaller, and
    typing-extensions versions is known to be incompatible.
    """

    for combi in AUTO_SKIPS:
        if (
            (
                python_version is None
                or combi.python is any
                or combi.python == python_version
            )
            and (
                pyinstaller_version is None
                or combi.pyinstaller is any
                or combi.pyinstaller == pyinstaller_version
            )
            and (
                typing_extensions_version is None
                or combi.typing_extensions is any
                or combi.typing_extensions == typing_extensions_version
            )
        ):
            return True
    return False


# HELPER: REQUIRE PKG_RESSOURCES -----------------------------------------------


def require_pkg_resources(pyinstaller_version: str) -> bool:
    """
    Return True if the given PyInstaller version requires the pkg_resources
    workaround, which is the case for all versions < 6.0.
    """
    return pyinstaller_version in [
        "==5.0",
        "==5.5",
        "==5.13",
        "<6.0",
    ]


# HELPER: SOFTEN FAIL IN PRE-RELEASE PYTHON ------------------------------------


def softfail_prerelease(func):
    """Decorator inserted after @nox.session to wrap prerelease logic."""
    import shlex
    import nox.command
    import functools

    @functools.wraps(func)
    def wrapper(session: nox.Session, *args, **kwargs):
        result: str | None = session.run(
            *shlex.split(
                'python -c "import sys;print(sys.version_info.releaselevel)"'
            ),
            silent=True,
        )
        if not result:
            session.error("Unable to detect release level of Python install")
        unstable: bool = result.strip() not in ("final", "candidate")
        # --- run the wrapped session as usual ---
        if not unstable:
            return func(session, *args, **kwargs)
        # --- prerelease-aware execution ---
        try:
            return func(session, *args, **kwargs)
        except nox.command.CommandFailed as e:
            # --- prerelease-aware error handling ---
            if unstable:
                title = "Downgraded pre-release failure"
                print(
                    f"::warning title={title}::"
                    f"{title} for session {session.name}: {e}"
                )
                session.skip("Pre-release Python soft fail")
            raise

    return wrapper


# SELF CHECK -------------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["self_check", "entrypoint"],
    requires=[
        "_self_check_Python_versions",
        "_self_check_new_PyInstaller",
        "_self_check_new_typing_extensions",
    ],
)
def self_check(session: nox.Session) -> None:
    """
    Run all self-checks to ensure the noxfile is up to date.
    """
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
    Check if all supported Python versions are tested.
    """
    pyproject = nox.project.load_toml("pyproject.toml")
    classifieers: list[str] = pyproject.get("project", {}).get(
        "classifiers", []
    )
    toml_versions: list[str] = [
        line.removeprefix("Programming Language :: Python :: ")
        for line in classifieers
        if line.startswith("Programming Language :: Python :: 3.")
    ]
    if set(PYTHON_VERSION_MATRIX) < set(toml_versions):
        session.error(
            "PYTHON_VERSION_MATRIX and pyproject.toml classifiers must match"
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


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["lint", "entrypoint"],
)
def flake8(session: nox.Session) -> None:
    """
    Lint with flake8.
    """
    session.install("-U", "flake8")
    session.run("python", "-m", "flake8", "./src")


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["lint", "entrypoint"],
)
def ruff_check(session: nox.Session) -> None:
    """
    Lint with ruff.
    """
    session.install("-U", "ruff")
    session.run("ruff", "check", "./src")


# FORMAT CHECKS ----------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["lint", "entrypoint"],
)
def ruff_format_check(session: nox.Session) -> None:
    """
    Check formatting with ruff.
    """
    session.install("-U", "ruff")
    session.run("ruff", "format", "--check", "./src")


# FORMATTERS -------------------------------------------------------------------


@nox.session(
    default=False,
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["format"],
)
def ruff_format(session: nox.Session) -> None:
    """
    Format code with ruff.
    """
    session.install("-U", "ruff")
    session.run("ruff", "format", "./src")


# TYPE CHECKERS ----------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_VERSION_MATRIX,
    tags=["typecheck", "mypy", "entrypoint"],
)
@softfail_prerelease
def mypy(session: nox.Session) -> None:
    """
    Typecheck with mypy.
    """
    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        "mypy",
        *nox.project.dependency_groups(pyproject, "types"),
        silent=False,
    )
    session.run("mypy", "src", "--strict")


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_VERSION_MATRIX,
    tags=["typecheck", "pyright", "entrypoint"],
)
@softfail_prerelease
def pyright(session: nox.Session) -> None:
    """
    Typecheck with pyright.
    """
    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        "pyright",
        *nox.project.dependency_groups(pyproject, "types"),
        silent=False,
    )
    session.run("pyright", "src")


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    python=PYTHON_VERSION_MATRIX,
    tags=["typecheck", "pyrefly", "entrypoint"],
)
@softfail_prerelease
def pyrefly(session: nox.Session) -> None:
    """
    Typecheck with pyrefly.
    """
    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        "pyrefly",
        *nox.project.dependency_groups(pyproject, "types"),
        silent=False,
    )
    session.run("pyrefly", "check", "src")


# TEST SOURCE CODE -------------------------------------------------------------


@nox.session(
    venv_backend=None,
    default=False,
    tags=["coverage"],
)
def clean_old_coverage(session: nox.Session) -> None:
    """
    Remove old coverage data to avoid mixing reports from different runs.
    """
    import os
    import shutil

    if os.path.exists("coverage_report"):
        shutil.rmtree("coverage_report", ignore_errors=False)


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["unittests", "coverage"],
    requires=["clean_old_coverage"],
)
@nox.parametrize(
    "python,pyinstaller_version,typing_extensions_version",
    [
        (python, pyinstaller_version, typing_extensions_version)
        for python in PYTHON_VERSION_MATRIX
        for pyinstaller_version in PYINSTALLER_VERSION_MATRIX
        for typing_extensions_version in TYPING_EXTENSIONS_VERSION_MATRIX
        if not skip_combination(
            python_version=python,
            pyinstaller_version=pyinstaller_version,
            typing_extensions_version=typing_extensions_version,
        )
    ],
)
@softfail_prerelease
def unittests_with_coverage(
    session: nox.Session,
    pyinstaller_version: str,
    typing_extensions_version: str,
) -> None:
    """
    Run the unit tests with coverage using pytest-cov.
    """
    # Pyinstaller < 6 needs a workaround to include the pkg_resources module
    # used in PyInstaller. It was formerly included in setuptools, but has been
    # removed in setuptools 82.
    additional_dependencies: list[str] = []
    if require_pkg_resources(pyinstaller_version):
        additional_dependencies = ["setuptools<82"]

    pyproject = nox.project.load_toml("pyproject.toml")
    session.install(
        "-U",
        "-e",
        ".",
        *nox.project.dependency_groups(pyproject, "test"),
        f"PyInstaller{pyinstaller_version}",
        f"typing-extensions{typing_extensions_version}",
        *additional_dependencies,
        silent=False,
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
        "-vv",
    )


# TEST GENERATED EXECUTABLE VERSIONINFO-----------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["integration-tests", "entrypoint"],
)
@nox.parametrize(
    "python,pyinstaller_version",
    [
        (python, pyinstaller_version)
        for python in PYTHON_VERSION_MATRIX
        for pyinstaller_version in PYINSTALLER_VERSION_MATRIX
        if not skip_combination(
            python_version=python,
            pyinstaller_version=pyinstaller_version,
        )
    ],
)
@softfail_prerelease
def integration_test(
    session: nox.Session,
    pyinstaller_version: str,
) -> None:
    """
    Run the integration tests.
    Compiles an executable and checks the versioninfo resource.
    """
    # Pyinstaller < 6 needs a workaround to include the pkg_resources module
    # used in PyInstaller. It was formerly included in setuptools, but has been
    # removed in setuptools 82.
    additional_dependencies: list[str] = []
    if require_pkg_resources(pyinstaller_version):
        additional_dependencies = ["setuptools<82"]

    session.install(
        "-U",
        "-e",
        ".",
        "pytest",
        f"PyInstaller{pyinstaller_version}",
        *additional_dependencies,
        silent=False,
    )

    session.run("pytest", "tests/test_integration.py", "-vv")


# BUILD DOCS -------------------------------------------------------------------


@nox.session(
    reuse_venv=REUSE_VENV,
    venv_backend=VENV_BACKEND,
    tags=["docs"],
)
def docs(session: nox.Session) -> None:
    """
    Build the documentation with pdoc.
    """
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
