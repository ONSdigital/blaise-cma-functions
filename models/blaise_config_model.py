import os

from dataclasses import dataclass


@dataclass
class BlaiseConfig:
    blaise_api_url: str

    @classmethod
    def from_env(cls):
        return cls(
            blaise_api_url=os.getenv("BLAISE_API_URL"),
        )