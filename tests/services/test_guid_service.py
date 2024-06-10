import logging
from unittest import mock

import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.guid_service import GUIDService
from tests.helpers import get_default_config
from utilities.custom_exceptions import GuidError


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@pytest.fixture()
def guid_service(blaise_service) -> GUIDService:
    return GUIDService(blaise_service=blaise_service)


@mock.patch.object(BlaiseService, "get_questionnaire")
def test_get_guid_returns_the_guid_as_a_string(
    get_questionnaire, guid_service, mock_get_questionnaire
):
    # Arrange
    get_questionnaire.return_value = mock_get_questionnaire
    blaise_server_park = "gusty"

    questionnaire_name = "LMS2309_GO1"

    # Act
    result = guid_service.get_guid(blaise_server_park, questionnaire_name)

    # Assert
    assert isinstance(result, str)
    assert result == "25615bf2-f331-47ba-9d05-6659a513a1f2"


@mock.patch.object(BlaiseService, "get_questionnaire")
def test_get_guid_logs_the_correct_message(
    get_questionnaire, guid_service, caplog, mock_get_questionnaire
):
    # Arrange
    get_questionnaire.return_value = mock_get_questionnaire
    blaise_server_park = "gusty"

    questionnaire_name = "LMS2309_GO1"

    # Act
    with caplog.at_level(logging.INFO):
        guid_service.get_guid(blaise_server_park, questionnaire_name)

    # Assert
    assert (
        "root",
        logging.INFO,
        "Got GUID 25615bf2-f331-47ba-9d05-6659a513a1f2 for questionnaire LMS2309_GO1",
    ) in caplog.record_tuples


@mock.patch.object(BlaiseService, "get_questionnaire")
def test_get_guid_logs_error_and_raises_guid_error_exception(
    get_questionnaire, guid_service, caplog
):
    # Arrange
    get_questionnaire.return_value = {}
    blaise_server_park = "gusty"

    questionnaire_name = "LMS2309_GO1"

    # Act
    with pytest.raises(GuidError) as err:
        guid_service.get_guid(blaise_server_park, questionnaire_name)

    # Assert
    error_message = (
        "Exception caught in get_guid(). "
        "Error getting GUID for questionnaire LMS2309_GO1: 'id'"
    )
    assert err.value.args[0] == error_message
    assert (
        "root",
        40,
        error_message,
    ) in caplog.record_tuples
