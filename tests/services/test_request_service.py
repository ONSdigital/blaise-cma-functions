import flask
import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.request_service import RequestService
from tests.helpers import get_default_config
from utilities.custom_exceptions import RequestError


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    def get_json(self):
        return self.json_data


def test_request_service_returns_valid_request_values(blaise_service):
    # arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
    )
    request_service = RequestService(mock_request, blaise_service)

    # act
    result = request_service.get_request_values()

    # assert
    assert result[0] == "IPS2402a"
    assert result[1] == "IPS Manager"


def test_request_service_logs_and_raises_request_error_exception_when_given_an_invalid_request(
    blaise_service, caplog
):
    # arrange
    mock_request = flask.Request.from_values(json=None)

    # act
    with pytest.raises(RequestError) as err:
        RequestService(request=mock_request, blaise_service=blaise_service)

    # assert
    error_message = (
        "Exception raised in RequestService.init(). "
        "Error getting json from request '<Request 'http://localhost/' [GET]>': "
        "415 Unsupported Media Type: Did not attempt to load JSON data because "
        "the request Content-Type was not 'application/json'."
    )
    assert err.value.args[0] == error_message
    assert (
        "root",
        40,
        error_message,
    ) in caplog.record_tuples


@pytest.mark.parametrize(
    "questionnaire_name, role",
    [
        (None, None),
        ("", None),
        (None, ""),
        ("", ""),
    ],
)
def test_request_service_logs_and_raises_request_error_exception_when_both_request_values_are_missing(
    questionnaire_name, role, blaise_service, caplog
):
    # arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": questionnaire_name, "role": role}
    )
    request_service = RequestService(
        request=mock_request, blaise_service=blaise_service
    )

    # act
    with pytest.raises(RequestError) as err:
        request_service.get_request_values()

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
def test_request_service_logs_and_raises_request_error_exception_when_questionnaire_name_is_missing(
    questionnaire_name, blaise_service, caplog
):
    # arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": questionnaire_name, "role": "IPS Manager"}
    )
    request_service = RequestService(
        request=mock_request, blaise_service=blaise_service
    )

    # act
    with pytest.raises(RequestError) as err:
        request_service.get_request_values()

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
def test_request_service_logs_and_raises_request_error_exception_when_role_is_missing(
    role, blaise_service, caplog
):
    # arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "role": role}
    )
    request_service = RequestService(
        request=mock_request, blaise_service=blaise_service
    )

    # act
    with pytest.raises(RequestError) as err:
        request_service.get_request_values()

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
        "DST", "BDSS", "SEL", "Editor", "foo", "IPS Manger", "IPS Interviewer", "IPS Feld Interviewer"
    ],
)
def test_request_service_logs_and_raises_request_error_exception_when_role_is_invalid(
        role, blaise_service, caplog
):
    # arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "role": role}
    )
    request_service = RequestService(
        request=mock_request, blaise_service=blaise_service
    )

    # act
    with pytest.raises(RequestError) as err:
        request_service.get_request_values()

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
