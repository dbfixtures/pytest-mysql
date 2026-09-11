"""Executor tests."""

import socket
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

import pytest

from pytest_mysql.exceptions import MySQLUnsupported
from pytest_mysql.executor import MySQLExecutor


@pytest.mark.parametrize(
    ("verstr", "version"),
    [
        (b"mysql_install_db Ver 5.7.21, for Linux on x86_64", "5.7.21"),
        (
            (b"mysqld  Ver 5.7.21-0ubuntu0.17.10.1 for Linux on x86_64 ((Ubuntu))"),
            "5.7.21",
        ),
        (b"mysql 5.5.55", "5.5.55"),
        (
            (
                b"mysqld  Ver 10.1.30-MariaDB-0ubuntu0.17.10.1 "
                b"for debian-linux-gnu on x86_64 (Ubuntu 17.10)"
            ),
            "10.1.30",
        ),
        (
            (b"mysqld  Ver 8.0.12 for macos10.13 on x86_64 (MySQL Community Server - GPL)"),
            "8.0.12",
        ),
        ((b"mysqld  Ver 5.7.23 for osx10.13 on x86_64 (Homebrew)"), "5.7.23"),
        ((b"\nmysqld  Ver 5.7.23 for osx10.13 on x86_64 (Homebrew)"), "5.7.23"),
    ],
)
def test_version_check(
    verstr: bytes, version: str, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Test executor's version property."""
    executor = MySQLExecutor(
        mysqld_safe=Path(""),
        mysqld=Path(""),
        admin_exec="",
        logfile_path="",
        params="",
        base_directory=tmp_path_factory.mktemp("pytest-mysql"),
        user="",
        host="",
        port=8838,
    )

    with patch("subprocess.check_output", lambda *args: verstr):
        assert version == executor.version()


@pytest.mark.parametrize(
    ("verstr", "implementation"),
    [
        (b"mysql_install_db Ver 5.7.21, for Linux on x86_64", "mysql"),
        (
            (b"mysqld  Ver 5.7.21-0ubuntu0.17.10.1 for Linux on x86_64 ((Ubuntu))"),
            "mysql",
        ),
        (b"mysql 5.5.55", "mysql"),
        (
            (
                b"mysqld  Ver 10.1.30-MariaDB-0ubuntu0.17.10.1 "
                b"for debian-linux-gnu on x86_64 (Ubuntu 17.10)"
            ),
            "mariadb",
        ),
        (b"mysql 8.0.12", "mysql"),
        (
            (b"Ver 8.0.12 for macos10.13 on x86_64 (MySQL Community Server - GPL)"),
            "mysql",
        ),
        (b"mysql 5.7.23", "mysql"),
        (
            (b"mysqld  Ver 5.7.23 for osx10.13 on x86_64 (Homebrew)"),
            "mysql",
        ),
    ],
)
def test_implementation(
    verstr: bytes, implementation: str, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Check detecting implementation."""
    executor = MySQLExecutor(
        mysqld_safe=Path(""),
        mysqld=Path(""),
        admin_exec="",
        logfile_path="",
        params="",
        base_directory=tmp_path_factory.mktemp("pytest-mysql"),
        user="",
        host="",
        port=8838,
    )

    with patch("subprocess.check_output", lambda *args: verstr):
        assert implementation == executor.implementation()


@pytest.mark.parametrize(
    "verstr",
    [
        b"mysql_install_db Ver 5.7.1, for Linux on x86_64",
        b"mysqld  Ver 5.7.1-0ubuntu0.17.10.1 for Linux on x86_64 ((Ubuntu))",
        b"mysql 5.5.55",
        (
            b"mysqld  Ver 10.1.30-MariaDB-0ubuntu0.17.10.1 "
            b"for debian-linux-gnu on x86_64 (Ubuntu 17.10)"
        ),
    ],
)
def test_exception_raised(verstr: bytes, tmp_path_factory: pytest.TempPathFactory) -> None:
    """Raise exception on not supported versions."""
    executor = MySQLExecutor(
        mysqld_safe=Path(""),
        mysqld=Path(""),
        admin_exec="",
        logfile_path="",
        params="",
        base_directory=tmp_path_factory.mktemp("pytest-mysql"),
        user="",
        host="",
        port=8838,
    )

    with (
        patch("subprocess.check_output", lambda *args, **kwargs: verstr),
        pytest.raises(MySQLUnsupported),
    ):
        executor.start()


@pytest.mark.parametrize(
    ("tcp_up", "socket_state", "started"),
    [
        (True, "listening", True),
        (True, "stale", False),
        (True, "missing", False),
        (False, "listening", False),
    ],
)
def test_after_start_check_waits_for_socket(
    tcp_up: bool,  # noqa: FBT001
    socket_state: str,
    started: bool,  # noqa: FBT001
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """The server counts as started only once its unix socket accepts connections."""
    executor = MySQLExecutor(
        mysqld_safe=Path(""),
        mysqld=Path(""),
        admin_exec="",
        logfile_path="",
        params="",
        base_directory=tmp_path_factory.mktemp("pytest-mysql"),
        user="",
        host="",
        port=8838,
    )
    with closing(socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)) as listener:
        if socket_state == "listening":
            listener.bind(executor.unixsocket)
            listener.listen(1)
        elif socket_state == "stale":
            Path(executor.unixsocket).touch()

        with patch("mirakuru.TCPExecutor.after_start_check", lambda _self: tcp_up):
            assert executor.after_start_check() is started
