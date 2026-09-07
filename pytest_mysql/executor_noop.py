"""Module containing Noop executor."""

from typing import Any, Literal


class NoopMySQLExecutor:
    """Noop Executor.

    Used to mimic in necessary scope the MySQL executor inside fixtures.
    """

    def __init__(
        self,
        user: str,
        host: str,
        port: int,
    ) -> None:
        """Initialize NoopMySQLExecutor."""
        self.user = user
        self.host = host
        self.port = port
        self.unixsocket = None

    def running(self) -> Literal[True]:
        """Check if process is running."""
        return True

    def start(self) -> None:
        """Do nothing starter."""

    def __enter__(self) -> None:
        """Do nothing enter method."""
        pass

    def __exit__(self, *args: object, **kwargs: Any) -> None:
        """Do nothing exit method."""
        pass
