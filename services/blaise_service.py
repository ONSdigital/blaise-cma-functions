import logging
from typing import Any, Dict

import blaise_restapi

from appconfig.config import Config
from models.donor_case_model import DonorCaseModel
from utilities.custom_exceptions import BlaiseError
from utilities.logging import function_name


class BlaiseService:
    def __init__(self, config: Config) -> None:
        self._config = config
        self.restapi_client = blaise_restapi.Client(
            f"http://{self._config.blaise_api_url}"
        )

        self.cma_serverpark_name = "cma"
        self.cma_questionnaire = "CMA_Launcher"

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
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting questionnaire '{questionnaire_name}': {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    def get_users(self, server_park: str) -> dict[str, Any]:
        try:
            users = self.restapi_client.get_users()
            logging.info(f"Got {len(users)} users from server park {server_park}")
            return users
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting users from server park {server_park}: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    def get_existing_donor_cases(self, guid: str):
        try:
            cases = self.restapi_client.get_questionnaire_data(
                self.cma_serverpark_name,
                self.cma_questionnaire,
                ["MainSurveyID", "CMA_ForWhom"],
            )
            return sorted(
                set(
                    [
                        entry["cmA_ForWhom"]
                        for entry in cases["reportingData"]
                        if entry["mainSurveyID"] == guid
                    ]
                )
            )
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting existing donor cases: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    def create_donor_case_for_user(self, donor_case_model: DonorCaseModel) -> None:
        try:
            self.restapi_client.create_multikey_case(
                self.cma_serverpark_name,
                self.cma_questionnaire,
                donor_case_model.key_names,
                donor_case_model.key_values,
                donor_case_model.data_fields,
            )
            logging.info(f"Created donor case for user '{donor_case_model.user}'")
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error creating donor case for user '{donor_case_model.user}': {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    def get_donor_cases_for_user(self, guid: str, user: str) -> []:
        try:
            cases = self.restapi_client.get_questionnaire_data(
                self.cma_serverpark_name,
                self.cma_questionnaire,
                ["MainSurveyID", "CMA_ForWhom", "CMA_Status", "id"],
            )
            donor_cases = []

            for entry in cases["reportingData"]:
                if (entry["mainSurveyID"] == guid and entry["cmA_Status"] == "" and entry["cmA_ForWhom"] == user):
                    donor_cases.append(entry)

            return donor_cases
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting existing cases: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)