import logging
from unittest import mock

import blaise_restapi
import flask

from appconfig.config import Config
from main import create_donor_cases, get_questionnaire_name, get_role
from models.donor_case_model import DonorCaseModel


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    def get_json(self):
        return self.json_data


@mock.patch("services.blaise_service.BlaiseService.get_questionnaire")
@mock.patch("services.blaise_service.BlaiseService.get_users")
@mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases")
@mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
def test_create_donor_case_is_called_the_correct_number_of_times_with_the_correct_information(
    mock_create_donor_case_for_user,
    mock_get_existing_donor_cases,
    mock_get_users,
    mock_get_questionnaire,
):
    # Arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
    )
    mock_get_questionnaire.return_value = {
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
    mock_get_users.return_value = [
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
    mock_get_existing_donor_cases.return_value = ["rich"]
    mock_donor_case_model = DonorCaseModel(
        "rich", "LMS2309_GO1", "25615bf2-f331-47ba-9d05-6659a513a1f2"
    )

    # Act
    create_donor_cases(mock_request)

    # Assert
    assert mock_create_donor_case_for_user.called_with(mock_donor_case_model)


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
@mock.patch.object(blaise_restapi.Client, "get_users")
@mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
@mock.patch.object(blaise_restapi.Client, "create_multikey_case")
def test_create_donor_case_is_called_the_correct_number_of_times_with_the_correct_information_when_mocking_the_blaise_service(
    mock_create_multikey_case,
    mock_get_questionnaire_data,
    mock_get_users,
    mock_get_questionnaire_for_server_park,
):
    # Arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
    )
    mock_get_questionnaire_for_server_park.return_value = {
        "name": "IPS2302a",
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
    mock_get_users.return_value = [
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
    mock_get_questionnaire_data.return_value = {
        "questionnaireName": "CMA_Launcher",
        "questionnaireId": "25615bf2-f331-47ba-9d05-6659a513a1f2",
        "reportingData": [
            {"cmA_ForWhom": "999"},
            {"cmA_ForWhom": "james"},
            {"cmA_ForWhom": "rich"},
        ],
    }

    # Act
    create_donor_cases(mock_request)

    # Assert
    assert mock_create_multikey_case.called_with(
        "cma",
        "CMA_Launcher",
        ["MainSurveyID", "ID"],
        ["25615bf2-f331-47ba-9d05-6659a513a1f2", "rich"],
        {
            "mainSurveyID": "25615bf2-f331-47ba-9d05-6659a513a1f2",
            "id": "rich",
            "cmA_ForWhom": "rich",
            "cmA_AllowSpawning": "1",
            "cmA_IsDonorCase": "1",
            "cmA_ContactData": "MainSurveyID    25615bf2-f331-47ba-9d05-6659a513a1f2    ID    rich    ContactInfoShort    IPS,April    CaseNote    This is the Donor Case. Select add case to spawn a new case with an empty shift.    Year    2023    Month    April    Stage    2303    ShiftNo    '",
        },
    )


@mock.patch("appconfig.config.Config.from_env")
@mock.patch.object(blaise_restapi.Client, "get_users")
def test_create_donor_case_raises_an_error_when_the_request_is_not_json(
    mock_get_users, mock_config, caplog
):
    # Arrange
    mock_request = None
    mock_config.return_value = Config(blaise_api_url="foo", blaise_server_park="bar")

    # Act
    with caplog.at_level(logging.INFO):
        create_donor_cases(mock_request)

    # Assert
    assert (
        "root",
        logging.ERROR,
        "Error creating IPS donor cases: 'NoneType' object has no attribute 'get_json'",
    ) in caplog.record_tuples


@mock.patch("appconfig.config.Config.from_env")
@mock.patch.object(blaise_restapi.Client, "get_users")
def test_create_donor_case_logs_when_questionnaire_name_value_is_none(
    mock_get_users, mock_config, caplog
):
    # Arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": None, "role": "IPS Manager"}
    )
    mock_config.return_value = Config(blaise_api_url="foo", blaise_server_park="bar")

    # Act
    with caplog.at_level(logging.INFO):
        create_donor_cases(mock_request)

    # Assert
    assert (
        "root",
        logging.ERROR,
        "Error creating IPS donor cases: Missing required fields: 'questionnaire_name'",
    ) in caplog.record_tuples


@mock.patch("appconfig.config.Config.from_env")
@mock.patch.object(blaise_restapi.Client, "get_users")
def test_create_donor_case_logs_when_questionnaire_name_value_is_missing(
    mock_get_users, mock_config, caplog
):
    # Arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "", "role": "IPS Manager"}
    )
    mock_config.return_value = Config(blaise_api_url="foo", blaise_server_park="bar")

    # Act
    with caplog.at_level(logging.INFO):
        create_donor_cases(mock_request)

    # Assert
    assert (
        "root",
        logging.ERROR,
        "Error creating IPS donor cases: Missing required fields: 'questionnaire_name'",
    ) in caplog.record_tuples


@mock.patch("appconfig.config.Config.from_env")
@mock.patch.object(blaise_restapi.Client, "get_users")
def test_create_donor_case_logs_when_role_value_is_none(
    mock_get_users, mock_config, caplog
):
    # Arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2306a", "role": None}
    )
    mock_config.return_value = Config(blaise_api_url="foo", blaise_server_park="bar")

    # Act
    with caplog.at_level(logging.INFO):
        create_donor_cases(mock_request)

    # Assert
    assert (
        "root",
        logging.ERROR,
        "Error creating IPS donor cases: Missing required fields: 'role'",
    ) in caplog.record_tuples


@mock.patch("appconfig.config.Config.from_env")
@mock.patch.object(blaise_restapi.Client, "get_users")
def test_create_donor_case_logs_when_role_value_is_missing(
    mock_get_users, mock_config, caplog
):
    # Arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2306a", "role": ""}
    )
    mock_config.return_value = Config(blaise_api_url="foo", blaise_server_park="bar")

    # Act
    with caplog.at_level(logging.INFO):
        create_donor_cases(mock_request)

    # Assert
    assert (
        "root",
        logging.ERROR,
        "Error creating IPS donor cases: Missing required fields: 'role'",
    ) in caplog.record_tuples


@mock.patch("appconfig.config.Config.from_env")
def test_create_donor_case_returns_message_and_500_status_code_when_config_is_empty(
    mock_config,
):
    # Arrange
    mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
    )
    mock_config.return_value = Config(blaise_api_url=None, blaise_server_park=None)

    # Act
    result = create_donor_cases(mock_request)

    # Assert
    assert result == ("Error creating IPS donor cases: Configuration error: Missing configurations - blaise_api_url, blaise_server_park", 500)



def test_get_questionnaire_name_returns_the_questionnaire_name():
    # Arrange
    mock_request = {"questionnaire_name": "IPS2402a", "role": "IPS Manager"}

    # Act
    result = get_questionnaire_name(mock_request)

    # Assert
    assert result == "IPS2402a"


def test_get_questionnaire_name_returns_the_role():
    # Arrange
    mock_request = {"questionnaire_name": "IPS2402a", "role": "IPS Field Manager"}

    # Act
    result = get_role(mock_request)

    # Assert
    assert result == "IPS Field Manager"
