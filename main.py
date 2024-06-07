import logging

import flask

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from services.guid_service import GUIDService
from services.user_service import UserService
from services.validation_service import ValidationService
from utilities.custom_exceptions import (
    BlaiseError,
    ConfigError,
    DonorCaseError,
    GuidError,
    QuestionnaireNotFound,
    RequestError,
    UsersError,
    UsersWithRoleNotFound,
)
from utilities.logging import setup_logger

setup_logger()


def create_donor_cases(request: flask.request):
    try:
        logging.info("Running Cloud Function - 'create_donor_cases'")
        validation_service = ValidationService()

        questionnaire_name, role = validation_service.get_valid_request_values(request)

        blaise_config = Config.from_env()
        validation_service.validate_config(blaise_config)
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
    except (RequestError, AttributeError, ValueError, ConfigError) as e:
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
