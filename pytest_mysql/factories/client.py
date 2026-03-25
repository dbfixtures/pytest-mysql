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
"""Client fixture factory for MySQL database."""

from typing import Any, Callable, Generator

import pytest
from _pytest.fixtures import FixtureRequest
from pymysql import Connection, OperationalError, ProgrammingError

from pytest_mysql.config import get_config
from pytest_mysql.exceptions import DatabaseExists
from pytest_mysql.executor import MySQLExecutor
from pytest_mysql.executor_noop import NoopMySQLExecutor


def mysql(
    process_fixture_name: str,
    passwd: str | None = None,
    dbname: str | None = None,
    charset: str = "utf8",
    collation: str = "utf8_general_ci",
) -> Callable[[FixtureRequest], Any]:
    """Client fixture factory for MySQL server.

    Factory. Create connection to mysql. If you want you can give a scope,
    default is 'session'.

    For charset and collation meaning,
    see `Database Character Set and Collation
    <https://dev.mysql.com/doc/refman/5.5/en/charset-database.html>`_

    :param str process_fixture_name: process fixture name
    :param str passwd: mysql server's password
    :param str dbname: database's name
    :param str charset: MySQL characterset to use by default
        for *tests* database
    :param str collation: MySQL collation to use by default
        for *tests* database

    :returns: function ``mysql_fixture`` with suit scope
    :rtype: func
    """

    def _connect(connect_kwargs: dict[str, Any], query_str: str, mysql_db: str) -> Connection:
        """Apply given query to a  given MySQLdb connection."""
        mysql_conn = Connection(**connect_kwargs)
        try:
            mysql_conn.query(query_str)
        except ProgrammingError as e:
            if "database exists" in str(e):
                raise DatabaseExists(
                    f"Database {mysql_db} already exists. There's some test "
                    f"configuration error. Either you start your own server "
                    f"with the database name used in tests, or you use two "
                    f"fixtures with the same database name on the same "
                    f"process fixture."
                ) from e
            raise
        return mysql_conn

    @pytest.fixture
    def mysql_fixture(
        request: FixtureRequest,
    ) -> Generator[Connection, None, None]:
        """Client fixture for MySQL server.

        #. Get config.
        #. Try to import MySQLdb package.
        #. Connect to mysql server.
        #. Create database.
        #. Use proper database.
        #. Drop database after tests.

        :param request: fixture request object

        :returns: connection to database
        """
        config = get_config(request)
        process: NoopMySQLExecutor | MySQLExecutor = request.getfixturevalue(process_fixture_name)
        if not process.running():
            process.start()

        mysql_user = process.user
        mysql_passwd = passwd or config["passwd"]
        mysql_db = dbname or config["dbname"]

        connection_kwargs: dict[str, Any] = {
            "host": process.host,
            "user": mysql_user,
            "passwd": mysql_passwd,
        }
        if process.unixsocket:
            connection_kwargs["unix_socket"] = process.unixsocket
        else:
            connection_kwargs["port"] = process.port

        query_str = (
            f"CREATE DATABASE `{mysql_db}` "
            f"DEFAULT CHARACTER SET {charset} "
            f"DEFAULT COLLATE {collation}"
        )
        try:
            mysql_conn: Connection = _connect(connection_kwargs, query_str, mysql_db)
        except OperationalError:
            # Fallback to mysql connection with root user
            connection_kwargs["user"] = "root"
            mysql_conn = _connect(connection_kwargs, query_str, mysql_db)
        mysql_conn.query(f"USE `{mysql_db}`")
        yield mysql_conn

        # clean up after test that forgot to fetch selected data
        if not mysql_conn.open:
            mysql_conn = Connection(**connection_kwargs)
        try:
            with mysql_conn.cursor() as cursor:
                cursor.fetchall()
        except Exception as e:
            print(str(e))
        query_drop_database = f"DROP DATABASE IF EXISTS `{mysql_db}`"
        mysql_conn.query(query_drop_database)
        mysql_conn.close()

    return mysql_fixture
