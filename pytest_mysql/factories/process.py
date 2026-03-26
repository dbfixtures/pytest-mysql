# Copyright (C) 2013 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-mysql.

# pytest-mysql is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-mysql is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-mysql.  If not, see <http://www.gnu.org/licenses/>.
"""Process fixture factory for MySQL database."""

from pathlib import Path
from typing import Callable, Generator
from warnings import warn

import pytest
from port_for import PortType, get_port
from pytest import FixtureRequest, TempPathFactory

from pytest_mysql.config import get_config
from pytest_mysql.executor import MySQLExecutor


def mysql_proc(
    mysqld_exec: Path | None = None,
    admin_executable: str | None = None,
    mysqld_safe: Path | None = None,
    host: str | None = None,
    user: str | None = None,
    port: PortType | None = -1,
    params: str | None = None,
    logs_prefix: str = "",
    install_db: str | None = None,
) -> Callable[[FixtureRequest, TempPathFactory], Generator[MySQLExecutor, None, None]]:
    """Process fixture factory for MySQL server.

    :param mysqld_exec: path to mysql executable
    :param admin_executable: path to mysql_admin executable
    :param mysqld_safe: path to mysqld_safe executable
    :param host: hostname
    :param user: user name
    :param port:
        exact port (e.g. '8000', 8000)
        randomly selected port (None) - any random available port
        [(2000,3000)] or (2000,3000) - random available port from a given range
        [{4002,4003}] or {4002,4003} - random of 4002 or 4003 ports
        [(2000,3000), {4002,4003}] -random of given range and set
    :param params: additional command-line mysqld parameters
    :param logs_prefix: prefix for log filename
    :param install_db: path to legacy mysql_install_db script
    :returns: function which makes a mysql process
    """

    @pytest.fixture(scope="session")
    def mysql_proc_fixture(
        request: FixtureRequest, tmp_path_factory: TempPathFactory
    ) -> Generator[MySQLExecutor, None, None]:
        """Process fixture for MySQL server.

        #. Get config.
        #. Initialize MySQL data directory
        #. `Start a mysqld server
            <https://dev.mysql.com/doc/refman/5.0/en/mysqld-safe.html>`_
        #. Stop server and remove directory after tests.
            `See <https://dev.mysql.com/doc/refman/5.6/en/mysqladmin.html>`_

        :param FixtureRequest request: fixture request object
        :param tmp_path_factory: pytest fixture for temporary directories
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor

        """
        config = get_config(request)
        mysql_mysqld = mysqld_exec or config.mysqld
        mysql_admin_exec = admin_executable or config.admin
        mysql_mysqld_safe = mysqld_safe or config.mysqld_safe
        mysql_port = get_port(port) or get_port(config.port)
        assert mysql_port
        mysql_host = host or config.host
        mysql_params = params or config.params
        mysql_install_db = install_db or config.install_db

        tmpdir = tmp_path_factory.mktemp(f"pytest-mysql-{request.fixturename}")

        if logs_prefix:
            warn(
                f"logfile_prefix factory argument is deprecated, "
                f"and will be dropped in future releases. All fixture related "
                f"data resides within {tmpdir}, and logs_prefix is only used, "
                f"if deprecated logsdir is configured",
                DeprecationWarning,
            )

        logfile_path = tmpdir / f"mysql-server.{port}.log"
        logsdir = config.logsdir
        if logsdir:
            warn(
                f"mysql_logsdir and --mysql-logsdir config option is "
                f"deprecated, and will be dropped in future releases. "
                f"All fixture related data resides within {tmpdir}",
                DeprecationWarning,
            )
            if logs_prefix:
                logfile_path = Path(logsdir) / f"{logs_prefix}mysql-server.{mysql_port}.log"

        mysql_executor = MySQLExecutor(
            mysqld_safe=mysql_mysqld_safe,
            mysqld=mysql_mysqld,
            admin_exec=mysql_admin_exec,
            logfile_path=str(logfile_path),
            base_directory=tmpdir,
            params=mysql_params,
            user=user or config.user or "root",
            host=mysql_host,
            port=mysql_port,
            install_db=mysql_install_db,
        )
        with mysql_executor:
            yield mysql_executor

    return mysql_proc_fixture
