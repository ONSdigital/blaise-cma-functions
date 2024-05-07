from unittest import mock

import blaise_restapi
import flask

from main import create_ips_donor_cases_processor
from models.donor_case_model import DonorCaseModel


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    def get_json(self):
        return self.json_data


@mock.patch("services.blaise_service.BlaiseService.get_questionnaire")
@mock.patch("services.blaise_service.BlaiseService.get_list_of_users")
@mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases")
@mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
def test_create_donor_case_for_users_gets_called_the_correct_numnber_of_times_with_the_correct_information(
    mock_create_donor_case_for_user,
    mock_get_existing_donor_cases,
        mock_get_list_of_users,
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
    mock_get_list_of_users.return_value = [
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
    create_ips_donor_cases_processor(mock_request)

    # Assert
    assert mock_create_donor_case_for_user.called_with(mock_donor_case_model)


@mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
@mock.patch.object(blaise_restapi.Client, "get_users")
@mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
@mock.patch.object(blaise_restapi.Client, "create_multikey_case")
def test_create_donor_case_for_users_gets_called_the_correct_numnber_of_times_with_the_correct_information_when_mocking_the_blaise_service(
    mock_create_multikey_case,
    mock_get_questionnaire_data,
        mock_get_list_of_users,
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
    mock_get_list_of_users.return_value = [
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
        "questionnaireName": "cma_launcher",
        "questionnaireId": "25615bf2-f331-47ba-9d05-6659a513a1f2",
        "reportingData": [
            {"cmA_ForWhom": "999"},
            {"cmA_ForWhom": "james"},
            {"cmA_ForWhom": "rich"},
        ],
    }

    # Act
    create_ips_donor_cases_processor(mock_request)

    # Assert
    assert mock_create_multikey_case.called_with(
        "cma",
        "cma_launcher",
        ["MainSurveyID", "ID"],
        ["25615bf2-f331-47ba-9d05-6659a513a1f2", "rich"],
        {
            "mainSurveyID": "25615bf2-f331-47ba-9d05-6659a513a1f2",
            "id": "rich",
            "cmA_ForWhom": "rich",
            "cmA_AllowSpawning": "1",
            "cmA_IsDonorCase": "1",
            "cmA_ContactData": "MainSurveyID    25615bf2-f331-47ba-9d05-6659a513a1f2    ID    rich    ContactInfoShort    IPS,April    CaseNote    This is the Donor Case. Select add case to spawn a new case with an empty shift.    pii.Year    2023    pii.Month    April    pii.Stage    2303    pii.ShiftNo    '",
        },
    )
