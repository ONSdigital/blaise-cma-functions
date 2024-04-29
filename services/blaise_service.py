import logging
import blaise_restapi

from typing import Dict, Any
from appconfig.config import Config


class BlaiseService:
    def __init__(self, config: Config):
        self._config = config
        self.restapi_client = blaise_restapi.Client(self._config.blaise_api_url)

    def get_questionnaire(self, server_park: str, questionnaire_name: str) -> Dict[str, Any]:
        try:
            questionnaire = self.restapi_client.get_questionnaire_for_server_park(server_park, questionnaire_name)
            logging.info(f"Got questionnaire {questionnaire_name}")
            return questionnaire
        except Exception as e:
            logging.error(f"Error getting questionnaire {questionnaire_name}: {e}")
            return ""

    def get_users(self, server_park: str) -> list[Dict[str, Any]]:
        try:
            users = self.restapi_client.get_users(server_park)
            logging.info(f"Got {len(users)} users from server park {server_park}")
            return users
        except Exception as e:
            logging.error(f"Error getting users from server park {server_park}: {e}")
            return []

    def get_existing_donor_cases(self):
        data = self.restapi_client.get_questionnaire_data("cma", "cma_launcher", "CMA_ForWhom")
        return sorted(set(entry["cmA_ForWhom"] for entry in data["reportingData"]))
