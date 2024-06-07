import logging
import re

import flask

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import RequestError


class ValidationService:
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
        self.validate_missing_values()
        self.validate_role()
        self.validate_questionnaire_name()

        return self.request_json["questionnaire_name"], self.request_json["role"]

    def validate_missing_values(self):
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

    def validate_role(self):
        valid_roles = ["IPS Manager", "IPS Field Interviewer"]
        if self.request_json["role"] not in valid_roles:
            error_message = (
                f"{self.request_json['role']} is not a valid role. "
                f"Please choose one of the following roles: {valid_roles}"
            )
            logging.error(error_message)
            raise RequestError(error_message)

    def validate_questionnaire_name(self):
        result = re.match(
            r"^[A-Za-z]{3}\d{4}.*$", self.request_json["questionnaire_name"]
        )
        if not result:
            error_message = (
                f"{self.request_json['questionnaire_name']} is not a valid questionnaire name format. "
                "Questionnaire name must start with 3 letters, followed by 4 numbers"
            )
            logging.error(error_message)
            raise RequestError(error_message)
        else:
            "yo"
