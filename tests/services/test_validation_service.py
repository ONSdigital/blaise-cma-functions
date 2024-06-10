from contextlib import contextmanager

import flask
import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.validation_service import ValidationService
from tests.helpers import get_default_config
from utilities.custom_exceptions import RequestError


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@contextmanager
def does_not_raise(ExpectedException):
    try:
        yield

    except ExpectedException as error:
        raise AssertionError(f"Raised exception {error} when it should not!")

    except Exception as error:
        raise AssertionError(f"An unexpected exception {error} raised.")


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    def get_json(self):
        return self.json_data


def test_validation_service_returns_questionnaire_name_and_role_when_given_a_valid_request():
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


def test_validation_service_does_not_raise_an_exception_when_given_a_valid_request():
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
def test_validation_service_logs_and_raises_validation_error_exception_when_both_validation_values_are_missing(
    questionnaire_name, role, caplog
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
def test_validation_service_logs_and_raises_validation_error_exception_when_questionnaire_name_is_missing(
    questionnaire_name, caplog
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
    "role",
    [None, ""],
)
def test_validation_service_logs_and_raises_validation_error_exception_when_role_is_missing(
    role, caplog
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
def test_validation_service_logs_and_raises_validation_error_exception_when_role_is_invalid(
    role, blaise_service, caplog
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
def test_validation_service_does_not_log_and_raises_validation_error_exception_when_role_is_valid(
    role
):
    # arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "role": role}
    )
    validation_service = ValidationService()

    # act
    with does_not_raise(RequestError):
        validation_service.get_valid_request_values(mock_request)


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
def test_validation_service_logs_and_raises_validation_error_exception_when_questionnaire_name_is_invalid(
    questionnaire_name, caplog
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
def test_validation_service_does_not_log_and_raise_validation_error_exception_when_questionnaire_name_is_valid(
    questionnaire_name, caplog
):
    # arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": questionnaire_name, "role": "IPS Manager"}
    )
    validation_service = ValidationService()

    # act
    with does_not_raise(RequestError):
        validation_service.get_valid_request_values(mock_request)


# TODO
# class TestCheckQuestionnaireExists:
#     @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
#     def test_check_questionnaire_exists_calls_the_rest_api_endpoint_with_the_correct_parameters(
#         self, _mock_rest_api_client, blaise_service
#     ):
#         # arrange
#         blaise_server_park = "gusty"
#         questionnaire_name = "IPS2306a"
#
#         # act
#         blaise_service.check_questionnaire_exists(
#             blaise_server_park, questionnaire_name
#         )
#
#         # assert
#         _mock_rest_api_client.assert_called_with(blaise_server_park, questionnaire_name)
#
#     @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
#     def test_get_questionnaire_returns_true_when_questionnaire_is_installed(
#         self, _mock_rest_api_client_questionnaire_exists_on_server_park, blaise_service
#     ):
#         # Arrange
#         _mock_rest_api_client_questionnaire_exists_on_server_park.return_value = True
#
#         blaise_server_park = "gusty"
#         questionnaire_name = "LMS2309_GO1"
#
#         # Act
#         result = blaise_service.check_questionnaire_exists(
#             blaise_server_park, questionnaire_name
#         )
#
#         # Assert
#         assert result is True
#
#     @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
#     def test_get_questionnaire_logs_and_raises_questionnaire_not_found_exception_when_questionnaire_is_not_installed(
#         self,
#         _mock_rest_api_client_questionnaire_exists_on_server_park,
#         blaise_service,
#         caplog,
#     ):
#         # Arrange
#         _mock_rest_api_client_questionnaire_exists_on_server_park.return_value = False
#
#         blaise_server_park = "gusty"
#         questionnaire_name = "LMS2309_GO1"
#
#         # Act
#         with pytest.raises(QuestionnaireNotFound) as err:
#             blaise_service.check_questionnaire_exists(
#                 blaise_server_park, questionnaire_name
#             )
#
#         # Assert
#         error_message = "Questionnaire LMS2309_GO1 is not installed in Blaise"
#         assert err.value.args[0] == error_message
#         assert (
#             "root",
#             logging.ERROR,
#             error_message,
#         ) in caplog.record_tuples
#
#     @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
#     def test_get_questionnaire_logs_and_raises_blaise_exception_when_client_fails(
#         self,
#         _mock_rest_api_client_questionnaire_exists_on_server_park,
#         blaise_service,
#         caplog,
#     ):
#         # Arrange
#         _mock_rest_api_client_questionnaire_exists_on_server_park.side_effect = (
#             Exception("Buttercup Cumbersnatch")
#         )
#
#         blaise_server_park = "gusty"
#         questionnaire_name = "LMS2309_GO1"
#
#         # Act
#         with pytest.raises(BlaiseError) as err:
#             blaise_service.check_questionnaire_exists(
#                 blaise_server_park, questionnaire_name
#             )
#
#         # Assert
#         error_message = (
#             "Exception caught in BlaiseService.check_questionnaire_exists(). "
#             "Error checking questionnaire 'LMS2309_GO1' exists: Buttercup Cumbersnatch"
#         )
#         assert err.value.args[0] == error_message
#         assert (
#             "root",
#             logging.ERROR,
#             error_message,
#         ) in caplog.record_tuples

# @mock.patch.object(BlaiseService, "get_users")
# def test_get_users_by_role_logs_and_raises_an_exception_when_no_users_are_found_with_a_given_role(
#     get_users, user_service, caplog
# ):
#     # Arrange
#     get_users.return_value = [
#         {
#             "name": "rich",
#             "role": "DST",
#             "serverParks": ["gusty", "cma"],
#             "defaultServerPark": "gusty",
#         },
#         {
#             "name": "sarah",
#             "role": "DST",
#             "serverParks": ["gusty"],
#             "defaultServerPark": "gusty",
#         },
#     ]
#     role = "IPS Field Interviewer"
#     blaise_server_park = "gusty"
#
#     # Act
#     with pytest.raises(UsersWithRoleNotFound) as err:
#         user_service.get_users_by_role(blaise_server_park, role)
#
#     # Assert
#     error_message = f"No users found with role '{role}'"
#     assert err.value.args[0] == error_message
#     assert (
#         "root",
#         logging.ERROR,
#         error_message,
#     ) in caplog.record_tuples
