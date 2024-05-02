import logging

import flask

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from services.guid_service import GUIDService
from services.user_service import UserService


def create_ips_donor_cases_processor(request: flask.Request):
    logging.info("Running Cloud Function - create_ips_donor_cases")

    blaise_config = Config.from_env()
    blaise_service = BlaiseService(config=blaise_config)

    blaise_server_park = blaise_config.blaise_server_park

    guid_service = GUIDService(blaise_service)
    user_service = UserService(blaise_service)
    donor_case_service = DonorCaseService(blaise_service)

    request_json = request.get_json()
    questionnaire_name = request_json["questionnaire_name"]
    role = request_json["role"]

    guid = guid_service.get_guid(blaise_server_park, questionnaire_name)
    users_with_role = user_service.get_users_by_role(role)
    donor_case_service.create_donor_case_for_users(
        questionnaire_name, guid, users_with_role
    )
    return "Done!", 200
