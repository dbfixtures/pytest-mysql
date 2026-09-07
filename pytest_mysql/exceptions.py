"""Pytest MySQL's exceptions."""


class PytestMySQLException(Exception):
    """Base plguin's exceptions."""


class MySQLUnsupported(PytestMySQLException):
    """Exception raised when an unsupported MySQL has been encountered."""


class VersionNotDetected(PytestMySQLException):
    """Exception raised when exector could not detect mysqls' version."""

    def __init__(self, output: str) -> None:
        """Create error message."""
        super().__init__(f"Could not detect version in {output}")


class SocketPathTooLong(PytestMySQLException):
    """Exception raised the socket path is over 103 chars.

    Raised on BSD/MacOS as Mysql will fail to start.
    """


class DatabaseExists(PytestMySQLException):
    """Raise this exception, when the database already exists."""
