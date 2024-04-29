from appconfig.config import Config
import pytest

from services.guid_service import GUIDService
from tests.helpers import get_default_config
from services.blaise_service import BlaiseService

from unittest import mock


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
def test_get_guid_returns_the_guid_as_a_string(get_questionnaire, guid_service):
    # Arrange
    get_questionnaire.return_value = {
        "name": "LMS2309_GO1",
        "id": "25615bf2-f331-47ba-9d05-6659a513a1f2",
        "serverParkName": "gusty",
        "installDate": "2024-04-24T09:49:34.2685322+01:00",
        "status": "Active",
        "dataRecordCount": 0,
        "hasData": False,
        "blaiseVersion": "5.9.9.2735",
        "nodes": [
            {
                "nodeName": "blaise-gusty-mgmt",
                "nodeStatus": "Active"
            },
            {
                "nodeName": "blaise-gusty-data-entry-1",
                "nodeStatus": "Active"
            },
            {
                "nodeName": "blaise-gusty-data-entry-2",
                "nodeStatus": "Active"
            }
        ]
    }

    questionnaire_name = "LMS2309_GO1"

    # Act
    result = guid_service.get_guid(questionnaire_name)

    # Assert
    assert isinstance(result, str)
    assert result == "25615bf2-f331-47ba-9d05-6659a513a1f2"
