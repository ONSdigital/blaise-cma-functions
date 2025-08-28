import logging
import re
from typing import Any

import blaise_restapi
from flask import Request

from appconfig.config import Config
from utilities.custom_exceptions import (
    BlaiseError,
    ConfigError,
    RequestError,
    UsersWithRoleNotFound,
)
from utilities.logging import function_name


class ValidationService:
    def __init__(self) -> None:
        self.request_json: dict[str, Any] = {}

    def get_valid_request_values_for_create_donor_cases(
        self, request: Request
    ) -> tuple[str, str]:
        self.validate_request_is_json(request)
        self.validate_request_values_are_not_empty()
        self.validate_questionnaire_name()
        self.validate_role()

        return self.request_json["questionnaire_name"], self.request_json["role"]

    def get_valid_request_values_for_reissue_new_donor_case(
        self, request: Request
    ) -> tuple[str, str]:
        self.validate_request_is_json(request)
        self.validate_request_values_are_not_empty_for_reissue_new_donor_case()
        self.validate_questionnaire_name()

        return self.request_json["questionnaire_name"], self.request_json["user"]

    def get_valid_request_value_for_get_users(self, request: Request) -> str:
        self.validate_request_is_json(request)
        self.validate_request_value_is_not_empty_for_get_users()
        self.validate_role()

        return self.request_json["role"]

    def validate_request_is_json(self, request):
        try:
            self.request_json = request.get_json()
        except Exception as e:
            error_message = (
                f"Exception raised in {function_name()}. "
                f"Error getting json from request '{request}': {e}"
            )
            logging.error(error_message)
            raise RequestError(error_message)

    def validate_request_values_are_not_empty(self):
        missing_values = []
        questionnaire_name = self.request_json["questionnaire_name"]
        role = self.request_json["role"]

        if questionnaire_name is None or questionnaire_name == "":
            missing_values.append("questionnaire_name")

        if role is None or role == "":
            missing_values.append("role")

        if missing_values:
            error_message = f"Missing required values from request: {missing_values}"
            logging.error(error_message)
            raise RequestError(error_message)

    def validate_request_values_are_not_empty_for_reissue_new_donor_case(self):
        missing_values = []
        questionnaire_name = self.request_json["questionnaire_name"]
        user = self.request_json["user"]

        if questionnaire_name is None or questionnaire_name == "":
            missing_values.append("questionnaire_name")

        if user is None or user == "":
            missing_values.append("user")

        if missing_values:
            error_message = f"Missing required values from request: {missing_values}"
            logging.error(error_message)
            raise RequestError(error_message)

    def validate_request_value_is_not_empty_for_get_users(self):
        missing_values = []
        role = self.request_json["role"]

        if role is None or role.strip() == "":
            missing_values.append("role")

        if missing_values:
            error_message = f"Missing required value from request: {missing_values}"
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

    def validate_role(self):
        valid_roles = ["IPS Manager", "IPS Field Interviewer", "IPS Pilot Interviewer"]
        if self.request_json["role"] not in valid_roles:
            error_message = (
                f"{self.request_json['role']} is not a valid role. "
                f"Please choose one of the following roles: {valid_roles}"
            )
            logging.error(error_message)
            raise RequestError(error_message)

    @staticmethod
    def validate_config(config):
        missing_configs = []
        if config.blaise_api_url is None or config.blaise_api_url == "":
            missing_configs.append("blaise_api_url")
        if config.blaise_server_park is None or config.blaise_server_park == "":
            missing_configs.append("blaise_server_park")

        if missing_configs:
            error_message = f"Missing required values from config: {missing_configs}"
            logging.error(error_message)
            raise ConfigError(error_message)

    @staticmethod
    def validate_questionnaire_exists(questionnaire_name: str, config: Config):
        server_park = config.blaise_server_park
        restapi_client = blaise_restapi.Client(f"http://{config.blaise_api_url}")

        try:
            restapi_client.questionnaire_exists_on_server_park(
                server_park, questionnaire_name
            )
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error checking questionnaire '{questionnaire_name}' exists: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)

    @staticmethod
    def validate_users_with_role_exist(users: list, role: str):
        if not users:
            error_message = f"No users found with role '{role}'"
            logging.error(error_message)
            raise UsersWithRoleNotFound(error_message)
