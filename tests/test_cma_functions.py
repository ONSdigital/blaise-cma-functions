from appconfig.config import Config
import pytest

from tests.helpers import get_default_config
from services.blaise_service import BlaiseService

from tests.helpers import mock_get_users
import blaise_restapi
from unittest import mock


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
def test_get_questionnaire_calls_the_rest_api_endpoint_with_the_correct_parameters(_mock_rest_api_client,
                                                                                   blaise_service):
    # arrange
    blaise_server_park = "gusty"
    questionnaire_name = "IPS2306a"

    # act
    blaise_service.get_questionnaire(blaise_server_park, questionnaire_name)

    # assert
    _mock_rest_api_client.assert_called_with(
        blaise_server_park, questionnaire_name
    )


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
def test_get_questionnaire_returns_a_dictionary_containing_questionnaire_info(
        _mock_rest_api_client_get_questionnaire_for_server_park, blaise_service
):
    # arrange
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

    blaise_server_park = "gusty"
    questionnaire_name = "LMS2309_GO1"

    # act
    result = blaise_service.get_questionnaire(blaise_server_park, questionnaire_name)

    # assert
    assert len(result) == 9
    assert isinstance(result, dict)

    assert result["name"] == "LMS2309_GO1"
    assert result["id"] == "25615bf2-f331-47ba-9d05-6659a513a1f2"
    assert result["serverParkName"] == "gusty"


def test_get_guid_returns_the_guid_as_a_string(blaise_service, mock_get_questionnaires):
    # Act
    result = blaise_service.get_quid(mock_get_questionnaires)

    # Assert
    assert isinstance(result, str)
    assert result == "25615bf2-f331-47ba-9d05-6659a513a1f2"


# @mock.patch.object(blaise_restapi.Client, "get_users")
# def test_get_users_calls_the_rest_api_endpoint_with_the_correct_parameters(_mock_rest_api_client, blaise_service):
#     # arrange
#     blaise_server_park = "gusty"
#
#     # act
#     blaise_service.get_users(blaise_server_park)
#
#     # assert
#     _mock_rest_api_client.assert_called_with(
#         blaise_server_park)

#
# @mock.patch.object(blaise_restapi.Client, "get_users")
# def test_get_users_returns_a_list_of_dictionaires_containing_user_info(
#         _mock_rest_api_client_get_users, blaise_service
# ):
#     # arrange
#     _mock_rest_api_client_get_users.return_value = [
#         {
#             "name": "rich",
#             "role": "DST",
#             "serverParks": [
#                 "gusty",
#                 "cma"
#             ],
#             "defaultServerPark": "gusty"
#         },
#         {
#             "name": "sarah",
#             "role": "DST",
#             "serverParks": [
#                 "gusty"
#             ],
#             "defaultServerPark": "gusty"
#         }
#     ]
#
#     blaise_server_park = "gusty"
#
#     # act
#     result = blaise_service.get_users(blaise_server_park)
#
#     # assert
#     assert len(result) == 2


def test_get_users_by_role_returns_a_list_of_users_with_a_given_role(blaise_service):
    # Arrange
    users = mock_get_users("IPS Field Interviewer")

    # Act
    result = blaise_service.get_users_by_role(users, "IPS Field Interviewer")

    # Assert
    assert len(result) == 1
    assert result == ["willij"]


def test_get_users_by_role_returns_empty_list_when_no_users_are_found_with_a_given_role(blaise_service):
    # Arrange
    users = mock_get_users("DST")

    # Act
    result = blaise_service.get_users_by_role(users, "IPS Field Interviewer")

    # Assert
    assert len(result) == 0
    assert result == []


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
def test_get_existing_donor_cases_calls_the_rest_api_endpoint_with_the_correct_parameters(_mock_rest_api_client, blaise_service):
    # arrange
    server_park = "cma"
    questionnaire_name = "cma_launcher"
    field_data = "CMA_ForWhom"

    # act
    blaise_service.get_existing_donor_cases()

    # assert
    _mock_rest_api_client.assert_called_with(
        server_park, questionnaire_name, field_data)


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
def test_get_existing_donor_cases_returns_a_list_of_unique_ids_(
        _mock_rest_api_client_get_questionnaire_data, blaise_service
):
    # arrange
    _mock_rest_api_client_get_questionnaire_data.return_value ={
        "questionnaireName": "cma_launcher",
        "questionnaireId": "b0425080-2470-49db-bb53-170633c4fbba",
        "reportingData": [
            {
                "cmA_ForWhom": "rich"
            },
            {
                "cmA_ForWhom": "james"
            },
            {
                "cmA_ForWhom": "rich"
            }
        ]
    }

    # act
    result = blaise_service.get_existing_donor_cases()