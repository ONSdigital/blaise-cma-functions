import logging

from flask import Request

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


def reissue_new_donor_case(request: Request) -> tuple[str, int]:
    try:
        logging.info("Running Cloud Function - 'reissue_new_donor_case'")
        validation_service = ValidationService()

        # Request Handler
        questionnaire_name, user = (
            validation_service.get_valid_request_values_for_reissue_new_donor_case(
                request
            )
        )

        # Config Handler
        blaise_config = Config.from_env()
        validation_service.validate_config(blaise_config)
        blaise_server_park = blaise_config.blaise_server_park

        # Blaise Handler
        blaise_service = BlaiseService(blaise_config)
        validation_service.validate_questionnaire_exists(
            questionnaire_name, blaise_config
        )

        # GUID Handler
        guid_service = GUIDService(blaise_service)
        guid = guid_service.get_guid(blaise_server_park, questionnaire_name)

        # User Handler
        user_service = UserService(blaise_service)
        user_service.get_user_by_name(blaise_server_park, user)

        # Donor Case Handler
        donor_case_service = DonorCaseService(blaise_service)
        donor_case_service.reissue_new_donor_case_for_user(
            questionnaire_name, guid, user
        )

        logging.info("Finished Running Cloud Function - 'reissue_new_donor_case'")
        return f"Successfully reissued new donor case for user: {user}", 200
    except (RequestError, AttributeError, ValueError, ConfigError) as e:
        error_message = f"Error reissuing IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 400
    except BlaiseError as e:
        error_message = f"Error reissuing IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 404
    except (GuidError, UsersError, DonorCaseError, Exception) as e:
        error_message = f"Error reissuing IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 500


def create_donor_cases(request: Request) -> tuple[str, int]:
    try:
        logging.info("Running Cloud Function - 'create_donor_cases'")
        validation_service = ValidationService()

        # Request Handler
        questionnaire_name, role = (
            validation_service.get_valid_request_values_for_create_donor_cases(request)
        )

        # Config Handler
        blaise_config = Config.from_env()
        validation_service.validate_config(blaise_config)
        blaise_server_park = blaise_config.blaise_server_park

        # Blaise Handler
        blaise_service = BlaiseService(blaise_config)
        validation_service.validate_questionnaire_exists(
            questionnaire_name, blaise_config
        )

        # GUID Handler
        guid_service = GUIDService(blaise_service)
        guid = guid_service.get_guid(blaise_server_park, questionnaire_name)

        # User Handler
        user_service = UserService(blaise_service)
        users_with_role = user_service.get_users_by_role(blaise_server_park, role)
        validation_service.validate_users_with_role_exist(users_with_role, role)

        # Donor Case Handler
        donor_case_service = DonorCaseService(blaise_service)
        donor_case_service.check_and_create_donor_case_for_users(
            questionnaire_name, guid, users_with_role
        )

        logging.info("Finished Running Cloud Function - 'create_donor_cases'")
        return f"Successfully created donor cases for user role: {role}", 200
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


def get_users_by_role(request: Request) -> tuple[list[str], int]:
    try:
        logging.info("Running Cloud Function - 'get_users'")
        validation_service = ValidationService()

        # Request Handler
        role = validation_service.get_valid_request_value_for_get_users(request)

        # Config Handler
        blaise_config = Config.from_env()
        validation_service.validate_config(blaise_config)
        blaise_server_park = blaise_config.blaise_server_park

        # Blaise Handler
        blaise_service = BlaiseService(blaise_config)

        # User Handler
        user_service = UserService(blaise_service)
        users_with_role = user_service.get_users_by_role(blaise_server_park, role)

        logging.info(
            f"Finished Running Cloud Function - 'get_users' Returned {users_with_role}"
        )
        return users_with_role, 200
    except (RequestError, AttributeError, ValueError, ConfigError) as e:
        error_message = f"Error retrieving users: {e}"
        logging.error(error_message)
        return [error_message], 400
    except BlaiseError as e:
        error_message = f"Error retrieving users: {e}"
        logging.error(error_message)
        return [error_message], 404
    except (UsersError, Exception) as e:
        error_message = f"Error retrieving users: {e}"
        logging.error(error_message)
        return [error_message], 500
