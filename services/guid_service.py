import logging

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import GuidError, BlaiseError


class GUIDService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def get_guid(self, server_park: str, questionnaire_name: str) -> str:
        try:
            questionnaire = self._blaise_service.get_questionnaire(
                server_park, questionnaire_name
            )
            guid = questionnaire["id"]
            logging.info(f"Got GUID {guid} for questionnaire {questionnaire_name}")
            return guid
        except BlaiseError as e:
            error_message = (
                f"BlaiseError caught in GUIDService.get_guid(). "
                f"Error getting GUID for questionnaire {questionnaire_name}: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(message=error_message)
        except Exception as e:
            error_message = (
                f"Generic Exception caught in get_guid(). "
                f"Error getting GUID for questionnaire {questionnaire_name}: {e}"
            )
            logging.error(error_message)
            raise GuidError(message=error_message)
