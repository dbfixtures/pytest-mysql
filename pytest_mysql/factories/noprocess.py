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

from typing import Callable, Generator, Optional

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_mysql.config import get_config
from pytest_mysql.executor_noop import NoopMySQLExecutor


def mysql_noproc(
    host: Optional[str] = None,
    port: Optional[int] = None,
    user: Optional[str] = None,
) -> Callable[[FixtureRequest], Generator[NoopMySQLExecutor, None, None]]:
    """Process fixture factory for MySQL server.

    :param str host: hostname
    :param int port: port name
    :param str user: user name
    :rtype: func
    :returns: function which makes a mysql process

    """

    @pytest.fixture(scope="session")
    def mysql_noproc_fixture(
        request: FixtureRequest,
    ) -> Generator[NoopMySQLExecutor, None, None]:
        """Process fixture for MySQL server.

        #. Get config.

        :param request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor

        """
        config = get_config(request)
        mysql_port = int(port or config.port or 3306)
        mysql_host = host or config.host
        mysql_user = user or config.user or "root"

        mysql_executor = NoopMySQLExecutor(
            user=mysql_user,
            host=mysql_host,
            port=mysql_port,
        )
        with mysql_executor:
            yield mysql_executor

    return mysql_noproc_fixture
