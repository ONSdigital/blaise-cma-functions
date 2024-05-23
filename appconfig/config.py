import os
from dataclasses import dataclass


@dataclass
class Config:
    blaise_api_url: str
    blaise_server_park: str
    gcloud_project: str
    region: str
    cloud_function_sa: str

    @classmethod
    def from_env(cls):
        return cls(
            blaise_api_url=os.getenv("BLAISE_API_URL"),
            blaise_server_park=os.getenv("BLAISE_SERVER_PARK"),
            gcloud_project=os.getenv("GCLOUD_PROJECT"),
            region=os.getenv("REGION"),
            cloud_function_sa=os.getenv("CLOUD_FUNCTION_SA"),
        )
