import logging
from typing import Any, Dict

import blaise_restapi

from appconfig.config import Config
from models.donor_case_model import DonorCaseModel


class BlaiseService:
    def __init__(self, config: Config):
        self._config = config
        self.restapi_client = blaise_restapi.Client(
            f"http://{self._config.blaise_api_url}"
        )

        self.serverpark_name = "cma"
        self.cma_questionnaire = "cma_launcher"

    def get_questionnaire(
        self, server_park: str, questionnaire_name: str
    ) -> Dict[str, Any]:
        try:
            questionnaire = self.restapi_client.get_questionnaire_for_server_park(
                server_park, questionnaire_name
            )
            logging.info(f"Got questionnaire '{questionnaire_name}'")
            return questionnaire
        except Exception as e:
            logging.error(f"Error getting questionnaire {questionnaire_name}: {e}")
            return None

    def get_users(self, server_park: str) -> list[Dict[str, Any]]:
        try:
            users = self.restapi_client.get_users(server_park)
            logging.info(f"Got {len(users)} users from server park {server_park}")
            return users
        except Exception as e:
            logging.error(f"Error getting users from server park {server_park}: {e}")
            return []

    def get_existing_donor_cases(self):
        cases = self.restapi_client.get_questionnaire_data(
            self.serverpark_name, self.cma_questionnaire, "CMA_ForWhom"
        )
        return sorted(set(entry["cmA_ForWhom"] for entry in cases["reportingData"]))

    def create_donor_case_for_user(self, donor_case_model: DonorCaseModel) -> None:
        self.restapi_client.create_multikey_case(
            self.serverpark_name,
            self.cma_questionnaire,
            donor_case_model.key_names,
            donor_case_model.key_values,
            donor_case_model.field_data,
        )
