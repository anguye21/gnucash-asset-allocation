import configparser
import os.path
from typing import Dict

from xdg.BaseDirectory import xdg_config_home


class InvalidConfigException(Exception):
    pass


class Config:
    CONFIG_FILE: str = os.path.join(
        xdg_config_home, "gnucash-asset-allocation/config.ini"
    )

    def __init__(self) -> None:
        if not os.path.exists(Config.CONFIG_FILE):
            raise InvalidConfigException(f"{Config.CONFIG_FILE} does not exist")

        config: configparser.ConfigParser = configparser.ConfigParser()

        with open(Config.CONFIG_FILE) as cf:
            config.read_string(cf.read())

        if "gnucash" not in config:
            raise InvalidConfigException("gnucash section no in config file")

        if "file" not in config["gnucash"]:
            raise InvalidConfigException("GnuCash file not specified in config file")

        if "account" not in config["gnucash"]:
            raise InvalidConfigException("account not specified in config file")

        if "allocation" not in config:
            raise InvalidConfigException("allocation section no in config file")

        self.file: str = config["gnucash"]["file"]
        self.file = os.path.expanduser(self.file)
        self.file = os.path.expandvars(self.file)

        self.account = config["gnucash"]["account"]

        self.allocation: Dict[str, float] = {}

        allocation_sum: float = 0

        for key in config["allocation"]:
            self.allocation[key.upper()] = float(config["allocation"][key])
            allocation_sum += self.allocation[key.upper()]

        if allocation_sum != 100:
            raise InvalidConfigException("allocation doesn't add up to 100%")
