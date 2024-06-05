import logging

import flask

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from services.guid_service import GUIDService
from services.user_service import UserService
from utilities.custom_exceptions import ConfigError, BlaiseError, GuidError, DonorCaseError
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
        error_message = f"Error creating IPS donor cases. AttributeError raised: {e}. "
        logging.error(error_message)
        return error_message, 400
    except ValueError as e:
        error_message = f"Error creating IPS donor cases. ValueError raised: {e}. "
        logging.error(error_message)
        return error_message, 400
    except ConfigError as e:
        error_message = f"Error creating IPS donor cases. Custom ConfigError raised: {e}"
        logging.error(error_message)
        return error_message, 400
    except BlaiseError as e:
        error_message = f"Error creating IPS donor cases. Custom BlaiseError raised: {e}"
        logging.error(error_message)
        return error_message, 404
    except GuidError as e:
        error_message = f"Error creating IPS donor cases. Custom GuidError raised: {e}"
        logging.error(error_message)
        return error_message, 500
    except DonorCaseError as e:
        error_message = f"Error creating IPS donor cases. Custom DonorCaseError raised: {e}. "
        logging.error(error_message)
        return error_message, 500
    except Exception as e:
        error_message = f"Error creating IPS donor cases: {e}"
        logging.error(error_message)
        return error_message, 500


def get_request_values(request_json):
    missing_values = []

    questionnaire_name = request_json["questionnaire_name"]
    if questionnaire_name is None or questionnaire_name == "":
        missing_values.append('questionnaire_name')

    role = request_json["role"]
    if role is None or role == "":
        missing_values.append('role')

    if missing_values:
        error_message = f"Missing required fields: {missing_values}"
        logging.error(error_message)
        raise ValueError(error_message)

    return questionnaire_name, role
