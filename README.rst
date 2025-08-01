.. image:: https://raw.githubusercontent.com/dbfixtures/pytest-mysql/master/logo.png
    :width: 100px
    :height: 100px

pytest-mysql
============

.. image:: https://img.shields.io/pypi/v/pytest-mysql.svg
    :target: https://pypi.python.org/pypi/pytest-mysql/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/wheel/pytest-mysql.svg
    :target: https://pypi.python.org/pypi/pytest-mysql/
    :alt: Wheel Status

.. image:: https://img.shields.io/pypi/pyversions/pytest-mysql.svg
    :target: https://pypi.python.org/pypi/pytest-mysql/
    :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/pytest-mysql.svg
    :target: https://pypi.python.org/pypi/pytest-mysql/
    :alt: License

What is this?
=============

This is a pytest plugin, that enables you to test your code that relies on a running MySQL Database.
It allows you to specify fixtures for MySQL process and client.

.. warning::

    Only MySQL 5.7.6 and up are supported. For older versions, please use pytest-mysql 2.0.3
    Although Pull Request to add back support for older MySQL versions are welcome.

How to use
==========

Plugin contains two fixtures

* **mysql** - it's a client fixture that has functional scope. After each test drops test database from MySQL ensuring repeatability.
* **mysql_proc** - session scoped fixture, that starts MySQL instance at it's first use and stops at the end of the tests.
* **mysql_noproc** - session scoped fixtures, that allows to connect to already existing MySQL instance, and cleans the database at the end of the tests

Simply include one of these fixtures into your tests fixture list.

You can also create additional mysql client and process fixtures if you'd need to:


.. code-block:: python

    from pytest_mysql import factories
    from getpass import getuser

    mysql_my_proc = factories.mysql_proc(
        port=None, user=getuser())
    mysql_my = factories.mysql('mysql_my_proc')

.. note::

    Each MySQL process fixture can be configured in a different way than the others through the fixture factory arguments.

Configuration
=============

You can define your settings in three ways, it's fixture factory argument, command line option and pytest.ini configuration option.
You can pick which you prefer, but remember that these settings are handled in the following order:

    * ``Fixture factory argument``
    * ``Command line option``
    * ``Configuration option in your pytest.ini file``

.. list-table:: Configuration options
   :header-rows: 1

   * - MySQL/MariaDB option
     - Fixture factory argument
     - Command line option
     - pytest.ini option
     - Noop process fixture
     - Default
   * - Path to executable
     - mysqld_exec
     - --mysql-mysqld
     - mysql_mysqld
     - -
     - mysqld
   * - Path to safe executable
     - mysqld_safe
     - --mysql-mysqld-safe
     - mysql_mysqld_safe
     - -
     - mysqld_safe
   * - Path to mysql_install_db for legacy installations
     - install_db
     - --mysql-install-db
     - mysql_install_db
     - -
     - mysql_install_db
   * - Path to Admin executable
     - admin_executable
     - --mysql-admin
     - mysql_admin
     - -
     - mysqladmin
   * - Database hostname
     - host
     - --mysql-host
     - mysql_host
     - yes
     - localhost
   * - Database port
     - port
     - --mysql-port
     - mysql_port
     - yes (3306)
     - random
   * - MySQL user to work with
     - user
     - --mysql-user
     - mysql_user
     - -
     - root
   * - User's password
     - passwd
     - --mysql-passwd
     - mysql_passwd
     - -
     -
   * - Test database name
     - dbname
     - --mysql-dbname
     - mysql_dbname
     - -
     - test
   * - Starting parameters
     - params
     - --mysql-params
     - mysql_params
     - -
     -
   * - Log directory location [DEPRECATED]
     - logsdir
     - --mysql-logsdir
     - mysql_logsdir
     - -
     - $TMPDIR


Example usage:

* pass it as an argument in your own fixture

    .. code-block:: python

        mysql_proc = factories.mysql_proc(
            port=8888)

* use ``--mysql-port`` command line option when you run your tests

    .. code-block::

        py.test tests --mysql-port=8888


* specify your port as ``mysql_port`` in your ``pytest.ini`` file.

    To do so, put a line like the following under the ``[pytest]`` section of your ``pytest.ini``:

    .. code-block:: ini

        [pytest]
        mysql_port = 8888

Examples
========

Populating database for tests
-----------------------------

With SQLAlchemy
+++++++++++++++

This example shows how to populate database and create an SQLAlchemy's ORM connection:

Sample below is simplified session fixture from
`pyramid_fullauth <https://github.com/fizyk/pyramid_fullauth/>`_ tests:

.. code-block:: python

    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.pool import NullPool
    from zope.sqlalchemy import register


    @pytest.fixture
    def db_session(mysql):
        """Session for SQLAlchemy."""
        from pyramid_fullauth.models import Base  # pylint:disable=import-outside-toplevel

        # assumes setting, these can be obtained from pytest-mysql config or mysql_proc
        connection = f'mysql+mysqldb://root:@127.0.0.1:3307/tests?charset=utf8'

        engine = create_engine(connection, echo=False, poolclass=NullPool)
        pyramid_basemodel.Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
        pyramid_basemodel.bind_engine(
            engine, pyramid_basemodel.Session, should_create=True, should_drop=True)

        yield pyramid_basemodel.Session

        transaction.commit()
        Base.metadata.drop_all(engine)


    @pytest.fixture
    def user(db_session):
        """Test user fixture."""
        from pyramid_fullauth.models import User
        from tests.tools import DEFAULT_USER

        new_user = User(**DEFAULT_USER)
        db_session.add(new_user)
        transaction.commit()
        return new_user


    def test_remove_last_admin(db_session, user):
        """
        Sample test checks internal login, but shows usage in tests with SQLAlchemy
        """
        user = db_session.merge(user)
        user.is_admin = True
        transaction.commit()
        user = db_session.merge(user)

        with pytest.raises(AttributeError):
            user.is_admin = False
.. note::

    See the original code at `pyramid_fullauth's conftest file <https://github.com/fizyk/pyramid_fullauth/blob/2950e7f4a397b313aaf306d6d1a763ab7d8abf2b/tests/conftest.py#L35>`_.
    Depending on your needs, that in between code can fire alembic migrations in case of sqlalchemy stack or any other code

Connecting to MySQL/MariaDB (in a docker)
-----------------------------------------

To connect to a docker run MySQL and run test on it, use noproc fixtures.

.. code-block:: sh

    docker run --name some-db -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -d mysql --expose 3306

.. code-block:: sh

    docker run --name some-db -e MARIADB_ALLOW_EMPTY_PASSWORD=yes -d mariadb --expose 3306

This will start MySQL in a docker container, however using a MySQL installed locally is not much different.

In tests, make sure that all your tests are using **mysql_noproc** fixture like that:

.. code-block:: python

    mysql_in_docker = factories.mysql_noproc()
    mysql = factories.mysql("mysql_in_docker")


    def test_mysql_docker(mysql):
        """Run test."""
        cur = mysql.cursor()
        cur.query("CREATE TABLE pet (name VARCHAR(20), owner VARCHAR(20), species VARCHAR(20), sex CHAR(1), birth DATE, death DATE);")
        mysql.commit()
        cur.close()

And run tests:

.. code-block:: sh

    pytest --mysql-host=127.0.0.1



Running on Docker/as root
=========================

MySQL and MariaDB refuse to run as root by default, but we can force them by setting user=root in the configuration file.

However most common and secure approach is to change user which runs tests on Docker:

.. code-block::

    USER nobody

This line should switch your docker process to run on user nobody. See `this comment for example <https://github.com/dbfixtures/pytest-mysql/issues/62#issuecomment-367975723>`_

Package resources
-----------------

* Bug tracker: https://github.com/dbfixtures/pytest-mysql/issues

Release
=======

Install pipenv and --dev dependencies first, Then run:

.. code-block::

    pipenv run tbump [NEW_VERSION]
