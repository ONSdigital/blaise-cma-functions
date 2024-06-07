import logging

import flask

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from services.guid_service import GUIDService
from services.user_service import UserService
from utilities.custom_exceptions import (
    BlaiseError,
    ConfigError,
    DonorCaseError,
    GuidError,
    QuestionnaireNotFound,
    UsersError,
    UsersWithRoleNotFound,
)
from utilities.logging import setup_logger

setup_logger()


def create_donor_cases(request: flask.request):
    try:
        logging.info("Running Cloud Function - 'create_donor_cases'")
        request_json = request.get_json()
        questionnaire_name, role = get_request_values(request_json)

        blaise_config = Config.from_env()
        blaise_config.validate_config(blaise_config)
        blaise_server_park = blaise_config.blaise_server_park

        blaise_service = BlaiseService(blaise_config)
        blaise_service.check_questionnaire_exists(
            blaise_server_park, questionnaire_name
        )

        guid_service = GUIDService(blaise_service)
        guid = guid_service.get_guid(blaise_server_park, questionnaire_name)

        user_service = UserService(blaise_service)
        users_with_role = user_service.get_users_by_role(blaise_server_park, role)

        donor_case_service = DonorCaseService(blaise_service)
        donor_case_service.check_and_create_donor_case_for_users(
            questionnaire_name, guid, users_with_role
        )

        return "Done!", 200
    except (AttributeError, ValueError, ConfigError) as e:
        error_message = f"Error creating IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 400
    except BlaiseError as e:
        error_message = f"Error creating IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 404
    except (QuestionnaireNotFound, UsersWithRoleNotFound) as e:
        error_message = f"Error creating IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 422
    except (GuidError, UsersError, DonorCaseError, Exception) as e:
        error_message = f"Error creating IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 500


def get_request_values(request_json):
    missing_values = []
    if (
        request_json["questionnaire_name"] is None
        or request_json["questionnaire_name"] == ""
    ):
        missing_values.append("questionnaire_name")
    if request_json["role"] is None or request_json["role"] == "":
        missing_values.append("role")

    if missing_values:
        error_message = f"Missing required values from request: {missing_values}"
        logging.error(error_message)
        raise ValueError(error_message)

    return request_json["questionnaire_name"], request_json["role"]
