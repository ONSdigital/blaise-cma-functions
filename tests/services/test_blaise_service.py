import logging
from unittest import mock

import blaise_restapi
import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from tests.helpers import get_default_config


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
def test_get_questionnaire_calls_the_rest_api_endpoint_with_the_correct_parameters(
    _mock_rest_api_client, blaise_service
):
    # arrange
    blaise_server_park = "gusty"
    questionnaire_name = "IPS2306a"

    # act
    blaise_service.get_questionnaire(blaise_server_park, questionnaire_name)

    # assert
    _mock_rest_api_client.assert_called_with(blaise_server_park, questionnaire_name)


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
def test_get_questionnaire_returns_a_dictionary_containing_questionnaire_info(
    _mock_rest_api_client_get_questionnaire_for_server_park, blaise_service
):
    # Arrange
    _mock_rest_api_client_get_questionnaire_for_server_park.return_value = {
        "name": "LMS2309_GO1",
        "id": "25615bf2-f331-47ba-9d05-6659a513a1f2",
        "serverParkName": "gusty",
        "installDate": "2024-04-24T09:49:34.2685322+01:00",
        "status": "Active",
        "dataRecordCount": 0,
        "hasData": False,
        "blaiseVersion": "5.9.9.2735",
        "nodes": [
            {"nodeName": "blaise-gusty-mgmt", "nodeStatus": "Active"},
            {"nodeName": "blaise-gusty-data-entry-1", "nodeStatus": "Active"},
            {"nodeName": "blaise-gusty-data-entry-2", "nodeStatus": "Active"},
        ],
    }

    blaise_server_park = "gusty"
    questionnaire_name = "LMS2309_GO1"

    # Act
    result = blaise_service.get_questionnaire(blaise_server_park, questionnaire_name)

    # Assert
    assert len(result) == 9
    assert isinstance(result, dict)

    assert result["name"] == "LMS2309_GO1"
    assert result["id"] == "25615bf2-f331-47ba-9d05-6659a513a1f2"
    assert result["serverParkName"] == "gusty"


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
def test_get_questionnaire_logs_the_correct_information(
    _mock_rest_api_client_get_questionnaire_for_server_park, blaise_service, caplog
):
    # Arrange
    _mock_rest_api_client_get_questionnaire_for_server_park.return_value = {
        "name": "LMS2309_GO1",
        "id": "25615bf2-f331-47ba-9d05-6659a513a1f2",
        "serverParkName": "gusty",
        "installDate": "2024-04-24T09:49:34.2685322+01:00",
        "status": "Active",
        "dataRecordCount": 0,
        "hasData": False,
        "blaiseVersion": "5.9.9.2735",
        "nodes": [
            {"nodeName": "blaise-gusty-mgmt", "nodeStatus": "Active"},
            {"nodeName": "blaise-gusty-data-entry-1", "nodeStatus": "Active"},
            {"nodeName": "blaise-gusty-data-entry-2", "nodeStatus": "Active"},
        ],
    }

    blaise_server_park = "gusty"
    questionnaire_name = "LMS2309_GO1"

    # Act
    with caplog.at_level(logging.INFO):
        blaise_service.get_questionnaire(blaise_server_park, questionnaire_name)

    # Assert
    assert (
        "root",
        logging.INFO,
        "Got questionnaire 'LMS2309_GO1'",
    ) in caplog.record_tuples


@mock.patch.object(blaise_restapi.Client, "get_users")
def test_get_users_calls_the_rest_api_endpoint_with_the_correct_parameters(
    _mock_rest_api_client, blaise_service
):
    # Arrange
    blaise_server_park = "gusty"

    # Act
    blaise_service.get_list_of_users(blaise_server_park)

    # Assert
    _mock_rest_api_client.assert_called_with(blaise_server_park)


@mock.patch.object(blaise_restapi.Client, "get_users")
def test_get_users_returns_a_list_of_dictionaries_logs_the_correct_information(
    _mock_rest_api_client_get_users, blaise_service, caplog, mock_get_list_of_users
):
    # Arrange
    _mock_rest_api_client_get_users.return_value = mock_get_list_of_users

    blaise_server_park = "gusty"

    # Act
    with caplog.at_level(logging.INFO):
        blaise_service.get_list_of_users(blaise_server_park)

    # Assert
    assert (
        "root",
        logging.INFO,
        "Got 2 users from server park gusty",
    ) in caplog.record_tuples


@mock.patch.object(blaise_restapi.Client, "get_users")
def test_get_users_returns_a_list_of_dictionaires_containing_user_info(
    _mock_rest_api_client_get_users, blaise_service, caplog, mock_get_list_of_users
):
    # Arrange
    _mock_rest_api_client_get_users.return_value = mock_get_list_of_users

    blaise_server_park = "gusty"

    # Act
    result = blaise_service.get_list_of_users(blaise_server_park)

    # Assert
    assert len(result) == 2
    assert result == [
        {
            "name": "rich",
            "role": "DST",
            "serverParks": ["gusty", "cma"],
            "defaultServerPark": "gusty",
        },
        {
            "name": "sarah",
            "role": "DST",
            "serverParks": ["gusty"],
            "defaultServerPark": "gusty",
        },
    ]


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
def test_get_existing_donor_cases_calls_the_rest_api_endpoint_with_the_correct_parameters(
    _mock_rest_api_client, blaise_service
):
    # Arrange
    server_park = "cma"
    questionnaire_name = "cma_launcher"
    field_data = "CMA_ForWhom"

    # Act
    blaise_service.get_existing_donor_cases()

    # Assert
    _mock_rest_api_client.assert_called_with(
        server_park, questionnaire_name, field_data
    )


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
def test_get_existing_donor_cases_returns_a_list_of_unique_ids_(
    _mock_rest_api_client_get_questionnaire_data, blaise_service
):
    # Arrange
    _mock_rest_api_client_get_questionnaire_data.return_value = {
        "questionnaireName": "cma_launcher",
        "questionnaireId": "b0425080-2470-49db-bb53-170633c4fbba",
        "reportingData": [
            {"cmA_ForWhom": "rich"},
            {"cmA_ForWhom": "james"},
            {"cmA_ForWhom": "rich"},
        ],
    }

    # Act
    result = blaise_service.get_existing_donor_cases()

    # Assert
    assert len(result) == 2
    assert result == ["james", "rich"]
