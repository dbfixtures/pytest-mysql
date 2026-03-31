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
"""Plugin definition."""

from pytest import Parser

from pytest_mysql import factories

# pylint:disable=invalid-name
_help_mysqld = "Path to MySQLd executable"
_help_admin = "Path to MySQL's admin executable"
_help_install_db = "Path to MySQL's legacy install_db script (also used in MariaDB)"
_help_mysqld_safe = "Path to MySQL's init executable"
_help_logsdir = "[DEPRECATED] Logs directory location"
_help_host = "Host at which MySQL will accept connections"
_help_port = "Port at which MySQL will accept connections"
_help_port_search_count = "Number of times, pytest-mysql will search for free port"
_help_user = "MySQL username"
_help_passwd = "MySQL password"
_help_dbname = "Test database name"
_help_params = "Starting parameters for the MySQL"


def pytest_addoption(parser: Parser) -> None:
    """Plugin configuration."""
    parser.addini(name="mysql_mysqld", help=_help_mysqld, default="mysqld")
    parser.addoption(
        "--mysql-mysqld",
        action="store",
        metavar="path",
        dest="mysql_mysqld",
        help=_help_mysqld,
    )

    parser.addini(name="mysql_mysqld_safe", help=_help_mysqld_safe, default="mysqld_safe")
    parser.addoption(
        "--mysql-mysqld-safe",
        action="store",
        metavar="path",
        dest="mysql_mysqld_safe",
        help=_help_mysqld_safe,
    )

    parser.addini(name="mysql_admin", help=_help_admin, default="mysqladmin")
    parser.addoption(
        "--mysql-admin",
        action="store",
        metavar="path",
        dest="mysql_admin",
        help=_help_admin,
    )

    parser.addini(
        name="mysql_install_db",
        help=_help_install_db,
        default="mysql_install_db",
    )
    parser.addoption(
        "--mysql-install-db",
        action="store",
        metavar="path",
        dest="mysql_install_db",
        help=_help_install_db,
    )

    parser.addini(name="mysql_host", help=_help_host, default="localhost")
    parser.addoption(
        "--mysql-host",
        action="store",
        dest="mysql_host",
        help=_help_host,
    )

    parser.addini(
        name="mysql_port",
        help=_help_port,
        default=None,
    )
    parser.addoption("--mysql-port", action="store", dest="mysql_port", help=_help_port)

    parser.addini(
        name="mysql_port_search_count", type="int", help=_help_port_search_count, default=5
    )
    parser.addoption(
        "--mysql-port-search-count",
        action="store",
        type=int,
        dest="mysql_port_search_count",
        help=_help_port_search_count,
    )

    parser.addini(name="mysql_user", help=_help_user, default="root")
    parser.addoption("--mysql-user", action="store", dest="mysql_user", help=_help_user)

    parser.addini(name="mysql_passwd", help=_help_passwd, default="")
    parser.addoption("--mysql-passwd", action="store", dest="mysql_passwd", help=_help_passwd)

    parser.addini(name="mysql_dbname", help=_help_dbname, default="test")
    parser.addoption("--mysql-dbname", action="store", dest="mysql_dbname", help=_help_dbname)

    parser.addini(name="mysql_params", help=_help_params, default="")
    parser.addoption("--mysql-params", action="store", dest="mysql_params", help=_help_params)


mysql_proc = factories.mysql_proc()
mysql_noproc = factories.mysql_noproc()
mysql = factories.mysql("mysql_proc")

__all__ = ("pytest_addoption", "mysql_proc", "mysql_noproc", "mysql")
