import logging

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import BlaiseError, GuidError
from utilities.logging import function_name


class GUIDService:
    def __init__(self, blaise_service: BlaiseService) -> None:
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
            raise BlaiseError(e.message)
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting GUID for questionnaire {questionnaire_name}: {e}"
            )
            logging.error(error_message)
            raise GuidError(message=error_message)
