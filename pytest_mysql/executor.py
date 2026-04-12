"""Specified MySQL Executor."""

import platform
import re
import subprocess
from pathlib import Path
from typing import Any, Literal

from mirakuru import TCPExecutor
from packaging.version import parse

from pytest_mysql.exceptions import (
    MySQLUnsupported,
    SocketPathTooLong,
    VersionNotDetected,
)


class MySQLExecutor(TCPExecutor):
    """MySQL Executor for running MySQL server."""

    VERSION_RE = re.compile(r"(?:[a-z_ ]+)(Ver)? (?P<version>[\d.]+).*", re.I)
    IMPLEMENTATION_RE = re.compile(r".*MariaDB.*")

    def __init__(
        self,
        mysqld_safe: Path,
        mysqld: Path,
        admin_exec: str,
        logfile_path: str,
        params: str,
        base_directory: Path,
        user: str,
        host: str,
        port: int,
        timeout: int = 60,
        install_db: str | None = None,
    ) -> None:
        """Specialised Executor to run and manage MySQL server process.

        :param mysqld_safe: path to mysqld_safe executable
        :param mysqld: path to mysqld executable
        :param admin_exec: path to mysqladmin executable
        :param logfile_path: where the server shoyld wrute it's logs
        :param params: string containing additional starting parameters
        :param base_directory: base directory where the temporary files,
            database files, socket and pid will be placed in.
        :param user: mysql username
        :param host: server's host
        :param port: server's port
        :param timeout: executor's timeout for start and stop actions
        :param install_db:
        """
        self.mysqld_safe = mysqld_safe
        self.mysqld = mysqld
        self.install_db = install_db
        self.admin_exec = admin_exec
        self.base_directory = base_directory
        self.datadir = self.base_directory / f"mysqldata_{port}"
        self.datadir.mkdir()
        self.pidfile = self.base_directory / f"mysql-server.{port}.pid"
        self.unixsocket = str(self.base_directory / f"mysql.{port}.sock")
        self.logfile_path = logfile_path
        self.user = user
        self._initialised = False
        command = (
            f"{self.mysqld_safe} "
            f"--datadir={self.datadir} "
            f"--pid-file={self.pidfile} "
            f"--port={port} "
            f"--user={self.user} "
            f"--socket={self.unixsocket} "
            f"--log-error={self.logfile_path} "
            f"--tmpdir={self.base_directory} "
            f"--skip-syslog {params}"
        )
        super().__init__(command, host, port, timeout=timeout)

    def version(self) -> str:
        """Read MySQL's version."""
        version_output = subprocess.check_output([self.mysqld, "--version"]).decode("utf-8")
        matches = self.VERSION_RE.search(version_output)
        if not matches:
            raise VersionNotDetected(version_output)
        return matches.groupdict()["version"]

    def implementation(self) -> Literal["mariadb", "mysql"]:
        """Detect MySQL Implementation."""
        version_output = subprocess.check_output([self.mysqld, "--version"]).decode("utf-8")
        if self.IMPLEMENTATION_RE.search(version_output):
            return "mariadb"
        return "mysql"

    def initialize_mysqld(self) -> None:
        """Initialise mysql directory.

        #. Remove mysql directory if exist.
        #. `Initialize MySQL data directory
            <https://dev.mysql.com/doc/refman/5.7/en/data-directory-initialization-mysqld.html>`_

        :param str mysql_init: mysql_init executable
        :param str datadir: path to datadir
        :param str base_directory: path to base_directory

        """
        if self._initialised:
            return
        init_command = [
            str(self.mysqld),
            "--initialize-insecure",
            f"--datadir={self.datadir}",
            f"--tmpdir={self.base_directory}",
            f"--log-error={self.logfile_path}",
        ]
        subprocess.check_output(init_command)
        self._initialised = True

    def initialise_mysql_db_install(self) -> bool:
        """Initialize the mysql directory for older MySQL installations or MariaDB.

        #. Remove the mysql directory if it existed.
        #. `Initialize MySQL data directory
            <https://dev.mysql.com/doc/refman/5.7/en/data-directory-initialization-mysqld.html>`_

        :param str mysql_init: mysql_init executable
        :param str datadir: path to datadir
        :param str base_directory: path to base_directory

        """
        if not self.install_db:
            return False
        if self._initialised:
            return True
        init_command = [
            self.install_db,
            f"--user={self.user}",
            f"--datadir={self.datadir}",
            f"--tmpdir={self.base_directory}",
        ]
        subprocess.check_output(init_command)
        self._initialised = True
        return True

    def start(self) -> "MySQLExecutor":
        """Trigger initialization during start."""
        self._check_socket_path()

        implementation = self.implementation()
        if implementation == "mysql" and parse(self.version()) > parse("5.7.6"):
            self.initialize_mysqld()
        elif implementation in ["mysql", "mariadb"]:
            if not self.initialise_mysql_db_install():
                raise MySQLUnsupported("mysqld_init path is missing.")
        else:
            raise MySQLUnsupported("Only MySQL and MariaDB servers are supported with MariaDB.")
        return super().start()

    def shutdown(self) -> None:
        """Send shutdown command to the server."""
        shutdown_command = [
            self.admin_exec,
            f"--socket={self.unixsocket}",
            f"--user={self.user}",
            "shutdown",
        ]
        try:
            subprocess.check_output(shutdown_command)
        except subprocess.CalledProcessError:
            # Fallback to using root user for shutdown
            shutdown_command = [
                self.admin_exec,
                f"--socket={self.unixsocket}",
                "--user=root",
                "shutdown",
            ]
            subprocess.check_output(shutdown_command)

    def stop(self, *args: Any, **kwargs: Any) -> "MySQLExecutor":
        """Stop the server."""
        self.shutdown()
        return super().stop(*args, **kwargs)

    def _check_socket_path(self) -> None:
        if platform.system() in ["Darwin", "FreeBSD]"] and len(self.unixsocket) > 103:
            raise SocketPathTooLong(
                f"Socket path '{self.unixsocket}' is too long, "
                f"please pass ie. `--basetemp=/tmp/pytest_mysql` to pytest"
            )
