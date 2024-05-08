import logging

import flask

import json

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from services.guid_service import GUIDService
from services.user_service import UserService


def create_ips_donor_cases_processor(request):
    try:
        logging.info("Running Cloud Function - create_ips_donor_cases")

        blaise_config = Config.from_env()
        blaise_service = BlaiseService(config=blaise_config)

        blaise_server_park = blaise_config.blaise_server_park

        guid_service = GUIDService(blaise_service)
        user_service = UserService(blaise_service)
        donor_case_service = DonorCaseService(blaise_service)

        request_json = request.get_json()
        questionnaire_name = request_json.get("questionnaire_name")
        role = request_json.get("role")

        if questionnaire_name is None or role is None:
            raise ValueError("Missing required fields: questionnaire_name and/or role")

        guid = guid_service.get_guid(blaise_server_park, questionnaire_name)
        users_with_role = user_service.get_users_by_role(blaise_server_park, role)
        donor_case_service.create_donor_case_for_users(
            questionnaire_name, guid, users_with_role
        )
        return "Done!", 200
    except Exception as e:
        logging.error(f"Error creating IPS donor cases: {e}")
        return "Error creating IPS donor cases", 500
