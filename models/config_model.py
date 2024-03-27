import os

from dataclasses import dataclass


@dataclass
class Config:
    blaise_server_park: str
    blaise_api_url: str

    @classmethod
    def from_env(cls):
        return cls(
            blaise_server_park=os.getenv("BLAISE_SERVER_PARK"),
            blaise_api_url=os.getenv("BLAISE_API_URL"),
        )