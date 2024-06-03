import logging

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import GuidError


class GUIDService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def get_guid(self, server_park: str, questionnaire_name: str) -> str:
        questionnaire = self._blaise_service.get_questionnaire(
            server_park, questionnaire_name
        )
        try:
            guid = questionnaire["id"]
            logging.info(f"Got GUID {guid} for questionnaire {questionnaire_name}")
            return guid
        except Exception as e:
            logging.error(
                f"Error getting GUID for questionnaire {questionnaire_name}: {e}"
            )
            raise GuidError(questionnaire_name=questionnaire_name)
