import logging

import flask

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from services.guid_service import GUIDService
from services.user_service import UserService
from utilities.custom_exceptions import ConfigError, BlaiseError, GuidError, BlaiseUsersError
from utilities.logging import setup_logger

setup_logger()


def create_donor_cases(request: flask.request):
    try:
        logging.info("Running Cloud Function - 'create_donor_cases'")
        request_json = request.get_json()
        questionnaire_name = get_questionnaire_name(request_json)
        role = get_role(request_json)

        blaise_config = Config.from_env()
        blaise_config.validate_config(blaise_config)
        blaise_server_park = blaise_config.blaise_server_park

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
    except AttributeError as e:
        error_message = (
            "Error creating IPS donor cases. "
            f"AttributeError raised: {e}. "
            "This error occurred because an expected attribute was not found, for example in a JSON object. "
            "Please ensure that the object being accessed is the correct type, has the required attributes, and they are correctly spelled."
        )
        logging.error(error_message)
        return error_message, 400
    except ValueError as e:
        error_message = (
            "Error creating IPS donor cases. "
            f"ValueError raised: {e}. "
            "This error occurred due to an invalid value encountered in the input. "
            "Please check the input values for correctness and try again."
        )
        logging.error(error_message)
        return error_message, 400
    except ConfigError as e:
        error_message = (
            "Error creating IPS donor cases. "
            f"Custom ConfigError raised: {e}. "
            "This error occurred because the required configuration values were missing. "
            "Please check the values are being passed correctly and try again."
        )
        logging.error(error_message)
        return error_message, 400
    except BlaiseError as e:
        error_message = (
            "Error creating IPS donor cases. "
            f"Custom BlaiseError raised: {e}. "
            "This error occurred because the rest api failed to get the questionnaire from Blaise. "
            "Please check the VMs are online, the questionnaire is installed, and try again."
        )
        logging.error(error_message)
        return error_message, 404
    except GuidError as e:
        error_message = (
            "Error creating IPS donor cases. "
            f"Custom GuidError raised: {e}. "
            "This error occurred because the GUID service failed. "
            "Please check the questionnaire has an ID and try again."
        )
        logging.error(error_message)
        return error_message, 500
    except BlaiseUsersError as e:
        error_message = (
            "Error creating IPS donor cases. "
            f"Custom BlaiseUsersError raised: {e}. "
            "This error occurred because the service to get users by role from Blaise failed. "
            "Please check the VMs are online, the users exist with the correct role, and try again."
        )
        logging.error(error_message)
        return error_message, 404
    except Exception as e:
        logging.error(f"Error creating IPS donor cases: {e}")
        return f"Error creating IPS donor cases: {e}", 500


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
