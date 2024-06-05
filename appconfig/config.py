import os
from dataclasses import dataclass

from utilities.custom_exceptions import ConfigError


@dataclass
class Config:
    blaise_api_url: str
    blaise_server_park: str

    @classmethod
    def from_env(cls):
        return cls(
            blaise_api_url=os.getenv("BLAISE_API_URL"),
            blaise_server_park=os.getenv("BLAISE_SERVER_PARK"),
        )

    @staticmethod
    def validate_config(config):
        missing_configs = []
        if config.blaise_api_url is None or config.blaise_api_url == "":
            missing_configs.append("blaise_api_url")
        if config.blaise_server_park is None or config.blaise_server_park == "":
            missing_configs.append("blaise_server_park")

        if missing_configs:
            raise ConfigError(missing_configs=missing_configs)
