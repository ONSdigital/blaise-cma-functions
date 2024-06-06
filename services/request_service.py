import logging

import flask

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import RequestError


class RequestService:
    def __init__(self, request: flask.request, blaise_service: BlaiseService) -> None:
        try:
            request_json = request.get_json()
        except Exception as e:
            error_message = (
                "Exception raised in RequestService.init(). "
                f"Error getting json from request '{request}': {e}"
            )
            logging.error(error_message)
            raise RequestError(error_message)

        self.blaise_service = blaise_service
        self.role = request_json.get("role")
        self.questionnaire_name = request_json.get("questionnaire_name")
