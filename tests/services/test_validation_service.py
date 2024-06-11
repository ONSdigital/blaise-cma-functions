from contextlib import contextmanager
from unittest import mock

import blaise_restapi
import flask
import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.validation_service import ValidationService
from tests.helpers import get_default_config
from utilities.custom_exceptions import (
    BlaiseError,
    ConfigError,
    RequestError,
    UsersWithRoleNotFound,
)


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@contextmanager
def does_not_raise(expected_exception):
    try:
        yield

    except expected_exception as error:
        raise AssertionError(f"Raised exception {error} when it should not!")

    except Exception as error:
        raise AssertionError(f"An unexpected exception {error} raised.")


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    def get_json(self):
        return self.json_data


class TestGetValidRequestValues:
    def test_get_valid_request_values_returns_questionnaire_name_and_role_when_given_a_valid_request(
        self,
    ):
        # arrange
        validation_service = ValidationService()
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )

        # act
        result = validation_service.get_valid_request_values(mock_request)

        # assert
        assert result[0] == "IPS2402a"
        assert result[1] == "IPS Manager"

    def test_get_valid_request_values_does_not_raise_an_exception_when_given_a_valid_request(
        self,
    ):
        # arrange
        validation_service = ValidationService()
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )

        # assert
        with does_not_raise(Exception):
            validation_service.get_valid_request_values(mock_request)

    @pytest.mark.parametrize(
        "questionnaire_name, role",
        [
            (None, None),
            ("", None),
            (None, ""),
            ("", ""),
        ],
    )
    def test_get_valid_request_values_logs_and_raises_validation_error_exception_when_both_request_values_are_missing(
        self, questionnaire_name, role, caplog
    ):
        # arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "role": role}
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(RequestError) as err:
            validation_service.get_valid_request_values(mock_request)

        # assert
        error_message = (
            "Missing required values from request: ['questionnaire_name', 'role']"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "questionnaire_name",
        [None, ""],
    )
    def test_get_valid_request_values_logs_and_raises_validation_error_exception_when_questionnaire_name_is_missing(
        self, questionnaire_name, caplog
    ):
        # arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "role": "IPS Manager"}
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(RequestError) as err:
            validation_service.get_valid_request_values(mock_request)

        # assert
        error_message = "Missing required values from request: ['questionnaire_name']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "questionnaire_name",
        [
            "IPS123a",
            "IP2402a",
            "2402aIPS",
            "IPSmcIPSerson",
            "1232402a",
        ],
    )
    def test_get_valid_request_values_logs_and_raises_validation_error_exception_when_questionnaire_name_is_invalid(
        self, questionnaire_name, caplog
    ):
        # arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "role": "IPS Manager"}
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(RequestError) as err:
            validation_service.get_valid_request_values(mock_request)

        # assert
        error_message = (
            f"{questionnaire_name} is not a valid questionnaire name format. "
            "Questionnaire name must start with 3 letters, followed by 4 numbers"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "questionnaire_name",
        [
            "IPS2403a",
            "IPS2403b",
            "IPS2403",
            "LMS2406_TST",
            "OPN2604",
        ],
    )
    def test_get_valid_request_values_does_not_log_and_raise_validation_error_exception_when_questionnaire_name_is_valid(
        self, questionnaire_name, caplog
    ):
        # arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "role": "IPS Manager"}
        )
        validation_service = ValidationService()

        # act
        with does_not_raise(RequestError):
            validation_service.get_valid_request_values(mock_request)

    @pytest.mark.parametrize(
        "role",
        [None, ""],
    )
    def test_get_valid_request_values_logs_and_raises_validation_error_exception_when_role_is_missing(
        self, role, caplog
    ):
        # arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": role}
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(RequestError) as err:
            validation_service.get_valid_request_values(mock_request)

        # assert
        error_message = "Missing required values from request: ['role']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "role",
        [
            "DST",
            "BDSS",
            "SEL",
            "Editor",
            "foo",
            "IPS Manger",
            "IPS Interviewer",
            "IPS Feld Interviewer",
        ],
    )
    def test_get_valid_request_values_logs_and_raises_validation_error_exception_when_role_is_invalid(
        self, role, blaise_service, caplog
    ):
        # arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": role}
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(RequestError) as err:
            validation_service.get_valid_request_values(mock_request)

        # assert
        error_message = (
            f"{role} is not a valid role. "
            f"Please choose one of the following roles: ['IPS Manager', 'IPS Field Interviewer']"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "role",
        [
            "IPS Manager",
            "IPS Field Interviewer",
        ],
    )
    def test_get_valid_request_values_does_not_log_and_raise_validation_error_exception_when_role_is_valid(
        self, role
    ):
        # arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": role}
        )
        validation_service = ValidationService()

        # act
        with does_not_raise(RequestError):
            validation_service.get_valid_request_values(mock_request)


class TestValidateConfig:
    def test_validate_config_does_not_raise_an_exception_when_given_valid_config(self):
        # arrange
        validation_service = ValidationService()
        mock_config = Config(blaise_api_url="foo", blaise_server_park="bar")

        # assert
        with does_not_raise(ConfigError):
            validation_service.validate_config(mock_config)

    @pytest.mark.parametrize(
        "blaise_api_url, blaise_server_park",
        [
            (None, None),
            ("", None),
            (None, ""),
            ("", ""),
        ],
    )
    def test_validate_config_logs_and_raises_validation_error_exception_when_both_config_values_are_missing(
        self, blaise_api_url, blaise_server_park, caplog
    ):
        # arrange
        mock_config = Config(
            blaise_api_url=blaise_api_url, blaise_server_park=blaise_server_park
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(ConfigError) as err:
            validation_service.validate_config(mock_config)

        # assert
        error_message = "Missing required values from config: ['blaise_api_url', 'blaise_server_park']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_api_url",
        [None, ""],
    )
    def test_validate_config_logs_and_raises_validation_error_exception_when_blaise_api_url_is_missing(
        self, blaise_api_url, caplog
    ):
        # arrange
        mock_config = Config(blaise_api_url=blaise_api_url, blaise_server_park="bar")
        validation_service = ValidationService()

        # act
        with pytest.raises(ConfigError) as err:
            validation_service.validate_config(mock_config)

        # assert
        error_message = "Missing required values from config: ['blaise_api_url']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_server_park",
        [None, ""],
    )
    def test_validate_config_logs_and_raises_validation_error_exception_when_blaise_server_park_is_missing(
        self, blaise_server_park, caplog
    ):
        # arrange
        mock_config = Config(
            blaise_api_url="foo", blaise_server_park=blaise_server_park
        )
        validation_service = ValidationService()

        # act
        with pytest.raises(ConfigError) as err:
            validation_service.validate_config(mock_config)

        # assert
        error_message = "Missing required values from config: ['blaise_server_park']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples


class TestValidateQuestionnaireExists:
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    def test_validate_questionnaire_exists_does_not_raise_an_exception_when_questionnaire_exists(
        self, mock_questionnaire_exists_on_server_park
    ):
        # arrange
        mock_questionnaire_exists_on_server_park.return_value = {
            "questionnaire_name": "IPS2403a"
        }
        validation_service = ValidationService()
        mock_questionnaire_name = "IPS2403a"
        mock_config = Config(blaise_api_url="foo", blaise_server_park="bar")

        # assert
        with does_not_raise(BlaiseError):
            validation_service.validate_questionnaire_exists(
                mock_questionnaire_name, mock_config
            )

    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    def test_validate_questionnaire_exists_logs_and_raises_a_blaise_error_exception_when_rest_api_fails(
        self, mock_questionnaire_exists_on_server_park, caplog
    ):
        # arrange
        mock_questionnaire_exists_on_server_park.side_effect = Exception(
            "Bendybug Cannotkrump"
        )
        validation_service = ValidationService()
        mock_questionnaire_name = "IPS2403a"
        mock_config = Config(blaise_api_url="foo", blaise_server_park="bar")

        # act
        with pytest.raises(BlaiseError) as err:
            validation_service.validate_questionnaire_exists(
                mock_questionnaire_name, mock_config
            )

        # assert
        error_message = (
            "Exception caught in validate_questionnaire_exists(). "
            "Error checking questionnaire 'IPS2403a' exists: Bendybug Cannotkrump"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples


class TestValidateUsers:
    def test_validate_users_with_role_exist_does_not_raise_an_exception_when_users_with_role_exist(
        self,
    ):
        # arrange
        mock_users = ["Rich"]
        mock_role = "Lord and Saviour"
        validation_service = ValidationService()

        # assert
        with does_not_raise(BlaiseError):
            validation_service.validate_users_with_role_exist(mock_users, mock_role)

    def test_validate_users_with_role_exist_logs_and_raises_a_users_with_role_not_found_error_exception_when_no_users_with_role_exist(
        self, caplog
    ):
        # arrange
        mock_users = []
        mock_role = "Lord and Saviour"
        validation_service = ValidationService()

        # act
        with pytest.raises(UsersWithRoleNotFound) as err:
            validation_service.validate_users_with_role_exist(mock_users, mock_role)

        # assert
        error_message = "No users found with role 'Lord and Saviour'"
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples
