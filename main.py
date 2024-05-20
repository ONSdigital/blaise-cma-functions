import logging

import flask

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from services.guid_service import GUIDService
from services.user_service import UserService
from utilities.logging import setup_logger 

setup_logger()

def create_donor_cases(request: flask.request):
    try:
        logging.info("Running Cloud Function - 'create_donor_cases'")
        blaise_config = Config.from_env()
        blaise_server_park = blaise_config.blaise_server_park

        request_json = request.get_json()
        questionnaire_name = get_questionnaire_name(request_json)
        role = get_role(request_json)

        blaise_service = BlaiseService(config=blaise_config)
        guid_service = GUIDService(blaise_service)
        guid = guid_service.get_guid(blaise_server_park, questionnaire_name)

        user_service = UserService(blaise_service)
        users_with_role = user_service.get_users_by_role(blaise_server_park, role)

        donor_case_service = DonorCaseService(blaise_service)
        donor_case_service.check_and_create_donor_case_for_users(
            questionnaire_name, guid, users_with_role
        )
        return "Done!", 200
    except Exception as e:
        logging.error(f"Error creating IPS donor cases: {e}")
        return "Error creating IPS donor cases", 500


def get_role(request_json):
    role = request_json["role"]
    if role is None or role == "":
        raise ValueError("Missing required fields: 'role'")
    return role


def get_questionnaire_name(request_json):
    questionnaire_name = request_json["questionnaire_name"]
    if questionnaire_name is None or questionnaire_name == "":
        raise ValueError("Missing required fields: 'questionnaire_name'")
    return questionnaire_name