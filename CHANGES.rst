CHANGELOG
=========

.. towncrier release notes start

3.1.0 (2024-12-10)
==================

Breaking changes
----------------

- Drop support for Python 3.8


Features
--------

- Declare support for Python 3.13


Miscellaneus
------------

- `#550 <https://github.com/dbfixtures/pytest-mysql/issues/550>`_
- Fixed last piece of macosx environment setup after moving to pymysql
- Readme fix
- Update MySQL versions in CI


3.0.0 (2024-05-23)
==================

Breaking changes
----------------

- Replace mysqlclient with pymysql library.

  Installation of mysqlclient became more and more problematic on macosx which in turn proved to be hard to maintain on github-actions.

  PyMySQL is mostly API compatible so pytest-mysql usage is just changing import location with one exception for poorly documented client fixture closeup. (`#491 <https://github.com/dbfixtures/pytest-mysql/issues/491>`_)


Miscellaneus
------------

- `#481 <https://github.com/dbfixtures/pytest-mysql/issues/481>`_, `#527 <https://github.com/dbfixtures/pytest-mysql/issues/527>`_, `#530 <https://github.com/dbfixtures/pytest-mysql/issues/530>`_


2.5.0 (2023-10-30)
==================

Features
--------

- Add missing user param (`#474 <https://github.com/dbfixtures/pytest-mysql/issues/474>`_)
- Add support for Python 3.12 (`#480 <https://github.com/dbfixtures/pytest-mysql/issues/480>`_)


Miscellaneus
------------

- `#450 <https://github.com/dbfixtures/pytest-mysql/issues/450>`_, `#454 <https://github.com/dbfixtures/pytest-mysql/issues/454>`_, `#460 <https://github.com/dbfixtures/pytest-mysql/issues/460>`_, `#473 <https://github.com/dbfixtures/pytest-mysql/issues/473>`_, `#478 <https://github.com/dbfixtures/pytest-mysql/issues/478>`_, `#479 <https://github.com/dbfixtures/pytest-mysql/issues/479>`_, `#480 <https://github.com/dbfixtures/pytest-mysql/issues/480>`_


2.4.2 (2023-03-27)
==================

Bugfixes
--------

- Fix license configuration in pyproject.toml (`#426 <https://github.com/dbfixtures/pytest-mysql/issues/426>`_)


2.4.1 (2023-03-13)
==================

Bugfixes
--------

- Fix packaging mistake which did not included the subpackages. (`#417 <https://github.com/dbfixtures/pytest-mysql/issues/417>`_)


2.4.0 (2023-03-10)
==================

Breaking changes
----------------

- Dropped support for Python 3.7 (`#401 <https://github.com/dbfixtures/pytest-mysql/issues/401>`_)


Bugfixes
--------

- Raise exception with helpful message if unixsocket is too long on FreeBSD or MacOS system

  OSX gives out super long temp directories.  This isn't a problem until
  we run into an odd 103-character limit on the names of unix sockets
  `see this stackoverflow thread <https://unix.stackexchange.com/questions/367008/why-is-socket-path-length-limited-to-a-hundred-chars/367012#367012>`_.
  Here we warn and give the user a way out of it. (`#345 <https://github.com/dbfixtures/pytest-mysql/issues/345>`_)


Features
--------

- Added support to Python 3.11 (`#392 <https://github.com/dbfixtures/pytest-mysql/issues/392>`_)
- Add type hints and mypy checks (`#401 <https://github.com/dbfixtures/pytest-mysql/issues/401>`_)


Miscellaneus
------------

- Run tests on CI on macosx (`#245 <https://github.com/dbfixtures/pytest-mysql/issues/245>`_)
- Update example configuration in README (`#365 <https://github.com/dbfixtures/pytest-mysql/issues/365>`_)
- Readme fixes (`#372 <https://github.com/dbfixtures/pytest-mysql/issues/372>`_)
- Docstring fixes (`#378 <https://github.com/dbfixtures/pytest-mysql/issues/378>`_)
- Added towncrier to manage newsfragments (`#397 <https://github.com/dbfixtures/pytest-mysql/issues/397>`_)
- Migrate dependency management to pipenv (`#398 <https://github.com/dbfixtures/pytest-mysql/issues/398>`_)
- Move most of the package definition to pyproject.toml (`#399 <https://github.com/dbfixtures/pytest-mysql/issues/399>`_)
- Migrate automerge to a shared workflow using github app for short-lived tokens. (`#400 <https://github.com/dbfixtures/pytest-mysql/issues/400>`_)
- Use tbump to manage versioning (`#402 <https://github.com/dbfixtures/pytest-mysql/issues/402>`_)
- Updated codecov configuration:
  * Added token
  * Turned off pipeline failing if codecov upload fails (`#405 <https://github.com/dbfixtures/pytest-mysql/issues/405>`_)
- Run mariadb tests after MySQL tests run. (`#409 <https://github.com/dbfixtures/pytest-mysql/issues/409>`_)


2.3.1
=====

Bugs
----

- Now will accept correctly database names with hyphen

2.3.0
=====

Features
--------

- Import FixtureRequest from pytest, not private _pytest.
  Require at least pytest 6.2
- Replace tmpdir_factory with tmp_path_factory

Docs
----

- List mysql_noproc in README's fixtures list

Fixes
-----

- Database cleanup code will attempt to reconnect to mysql if test accidentally would close the connection

2.2.0
=====

Features
--------

- add `user` option to setup and tear down mysql process as non-privileged

Misc
----

- Add Python 3.10 to CI

2.1.0
=====

Features
--------

- `mysql_noproc` fixture to connect to already running mysql server
- raise more meaningful error when the test database already exists

Misc
----

- rely on `get_port` functionality delivered by `port_for`


Deprecation
-----------

- Deprecated `mysql_logsdir` ini configuration and `--mysql-logsdir` command option
- Deprecated `logs_prefix` process fixture factory setting

Misc
----

- Require minimum python 3.7
- Migrate CI to Github Actions

2.0.3
=====

- [enhancement] Do not assume that mysql executables are in /usr/bin

2.0.2
=====

- [enhancement] Preemptively read data after each test in mysql client fixture.
  This will make test run if the test itself forgot to fetch queried data.
- [enhnacement] Require at least mirakuru 2.3.0 - forced by changed stop method parameters change

2.0.1
=====

- [fix] Improved mysql version detection on osx
- [build] extracted xdist into separate stage on travis
- [build] have deployemt as separate stage on travis

2.0.0
=====

- [Enhancements] Add support for MySQL 5.7.6 and up with new configuration options. Legacy configuration supports older MySQL and MariaDB databases.
- [breaking] mysql_exec ini option replaced with mysql_mysqld_safe
- [breaking] --mysql-exec cmd option replaced with --mysql-mysqld-safe
- [breaking] replaced mysql_init ini option with mysql_install_db
- [breaking] replaced --mysql-init cmd option with --mysql-install-db 
- [breaking] added mysql_mysqld option and --mysql-mysqld cmd option

1.1.1
=====

- [enhancements] removed path.py dependency

1.1.0
=====

- [enhancement] change deprecated getfuncargvalaue to getfixturevalues, require at least pytest 3.0.0

1.0.0
=====

- [enhancements] create command line and pytest.ini configuration options for mysql's log directory location
- [enhancements] create command line and pytest.ini configuration options for mysql's starting parametetrs
- [enhancements] create command line and pytest.ini configuration options for mysql test database name
- [enhancements] create command line and pytest.ini configuration options for mysql's user password
- [enhancements] create command line and pytest.ini configuration options for mysql user
- [enhancements] create command line and pytest.ini configuration options for mysql host
- [enhancements] create command line and pytest.ini configuration options for mysql port
- [enhancements] create command line and pytest.ini configuration options for mysql's init executable
- [enhancements] create command line and pytest.ini configuration options for mysql's admin executable
- [enhancements] create command line and pytest.ini configuration options for mysql executable
- [enhancements] create command line and pytest.ini configuration options for mysql logsdir
