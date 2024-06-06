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

    # act
    result = RequestService(request=mock_request, blaise_service=blaise_service)

    # assert
    assert result.role == "IPS Manager"
    assert result.questionnaire_name == "IPS2402a"


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
