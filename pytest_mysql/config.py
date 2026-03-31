"""Config module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pytest import FixtureRequest


@dataclass
class MySQLConfig:
    """Configuration for pytest-mysql."""

    mysqld: Path
    mysqld_safe: Path
    admin: str
    host: str
    port: str
    port_search_count: int
    user: str
    passwd: str
    dbname: str
    params: str
    install_db: str


def get_config(request: FixtureRequest) -> MySQLConfig:
    """Return a pytest-mtsql config options."""

    def get_conf_option(option: str) -> Any:
        option_name = "mysql_" + option
        return request.config.getoption(option_name) or request.config.getini(option_name)

    return MySQLConfig(
        mysqld=Path(get_conf_option("mysqld")),
        mysqld_safe=Path(get_conf_option("mysqld_safe")),
        admin=get_conf_option("admin"),
        host=get_conf_option("host"),
        port=get_conf_option("port"),
        port_search_count=get_conf_option("port_search_count"),
        user=get_conf_option("user"),
        passwd=get_conf_option("passwd"),
        dbname=get_conf_option("dbname"),
        params=get_conf_option("params"),
        install_db=get_conf_option("install_db"),
    )
