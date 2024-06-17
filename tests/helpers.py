from appconfig.config import Config


def get_default_config() -> Config:
    return Config(blaise_api_url="blaise_api_url", blaise_server_park="gusty")
