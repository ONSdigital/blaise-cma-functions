import logging

import flask

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import RequestError


class RequestService:
    def __init__(self, request: flask.request, blaise_service: BlaiseService) -> None:
        self.blaise_service = blaise_service

        try:
            self.request_json = request.get_json()
        except Exception as e:
            error_message = (
                "Exception raised in RequestService.init(). "
                f"Error getting json from request '{request}': {e}"
            )
            logging.error(error_message)
            raise RequestError(error_message)

    def get_request_values(self):
        missing_values = []
        if (
                self.request_json["questionnaire_name"] is None
                or self.request_json["questionnaire_name"] == ""
        ):
            missing_values.append("questionnaire_name")
        if self.request_json["role"] is None or self.request_json["role"] == "":
            missing_values.append("role")

        if missing_values:
            error_message = f"Missing required values from request: {missing_values}"
            logging.error(error_message)
            raise RequestError(error_message)

        return self.request_json["questionnaire_name"], self.request_json["role"]
