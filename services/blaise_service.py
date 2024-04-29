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

    def get_quid(self, questionnaire: str) -> str:
        questionnaire_name = questionnaire["name"]
        try:
            guid = questionnaire["id"]
            logging.info(f"Got GUID {guid} for questionnaire {questionnaire_name}")
            return guid
        except Exception as e:
            logging.error(f"Error getting GUID for questionnaire {questionnaire_name}: {e}")
            return ""

    def get_users(self, server_park: str) -> list[Dict[str, Any]]:
        try:
            users = self.restapi_client.get_users(server_park)
            logging.info(f"Got {len(users)} users from server park {server_park}")
            return users
        except Exception as e:
            logging.error(f"Error getting users from server park {server_park}: {e}")
            return []

    def get_users_by_role(self, users: list, role: str) -> list[str] :
        return [user["name"] for user in users if user["role"] == role]

    def get_existing_donor_cases(self):
        return self.restapi_client.get_questionnaire_data("cma", "cma_launcher", "CMA_ForWhom").unique()

    def create_donor_cases(self, questionnaire_name: str, guid: str, users_with_role: list) -> None:
        existing_donor_cases = self.get_existing_donor_cases()
        for user in users_with_role:
            if not self.donor_case_exists(user, existing_donor_cases):
                # create_donor_case(field_interviewer, guid)
                return ""

    def donor_case_exists(self, user: str, users_with_existing_donor_cases) -> bool:
        try:
            if user not in users_with_existing_donor_cases:
                logging.info(f"Donor case does not exist for user {user}")
                return False
            else:
                logging.info(f"Donor case already exists for user {user}")
                return True
        except Exception as e:
            logging.error(f"Error checking donor case for user {user}: {e}")
