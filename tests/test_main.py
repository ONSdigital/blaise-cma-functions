import logging
from typing import Any
from unittest import mock

import blaise_restapi
import flask
import pytest

from appconfig.config import Config
from main import create_donor_cases, get_users_by_role, reissue_new_donor_case
from models.donor_case_model import DonorCaseModel
from utilities.custom_exceptions import (
    BlaiseError,
    DonorCaseError,
    GuidError,
    UsersError,
    UsersWithRoleNotFound,
)


class MockRequest:
    def __init__(self, json_data) -> None:
        self.json_data = json_data

    def get_json(self) -> dict[str, Any]:
        return self.json_data


class TestMainCreateDonorCaseFunction:

    @pytest.mark.parametrize(
        "role",
        [
            ("IPS Field Interviewer"),
            ("IPS Manager"),
            ("IPS Pilot Interviewer"),
        ],
    )
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    @mock.patch("services.blaise_service.BlaiseService.get_questionnaire")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    @mock.patch("services.blaise_service.BlaiseService.get_all_existing_donor_cases")
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("blaise_restapi.Client")
    def test_create_donor_case_returns_done_and_200_status_code_for_valid_request(
        self,
        mock_client,
        mock_config,
        mock_get_all_existing_donor_cases,
        mock_get_users,
        mock_get_questionnaire,
        mock_create_donor_case_for_user,
        role,
    ):
        # Arrange
        mock_config.return_value = Config(
            blaise_api_url="mock-blaise-api-url", blaise_server_park="gusty"
        )

        mock_client_instance = mock.Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.questionnaire_exists_on_server_park.return_value = True

        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": role}
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
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "DST",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "salleh",
                "role": "IPS Manager",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "michaelscarn",
                "role": "IPS Pilot Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]
        mock_get_all_existing_donor_cases.return_value = ["rich"]

        # Act
        response, status_code = create_donor_cases(mock_request)

        # Assert
        assert response == f"Successfully created donor cases for user role: {role}"
        assert status_code == 200


class TestMainCreateDonorCasesHandleRequestStep:

    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("services.blaise_service.BlaiseService.get_questionnaire")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    @mock.patch("services.blaise_service.BlaiseService.get_all_existing_donor_cases")
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    def test_create_donor_case_is_called_the_correct_number_of_times_with_the_correct_information(
        self,
        mock_create_donor_case_for_user,
        mock_get_all_existing_donor_cases,
        mock_get_users,
        mock_get_questionnaire,
        mock_config_from_env,
        mock_questionnaire_exists_on_server_park
    ):
        # Arrange
        mock_questionnaire_exists_on_server_park.return_value = True

        mock_config_from_env.return_value = Config(
            blaise_api_url="http://mock-url",
            blaise_server_park="gusty",
        )

        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "LMS2309_GO1", "role": "IPS Manager"}
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
                "role": "IPS Manager",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "IPS Manager",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]
        mock_get_all_existing_donor_cases.return_value = ["rich"]
        mock_donor_case_model = DonorCaseModel(
            "rich", "LMS2309_GO1", "25615bf2-f331-47ba-9d05-6659a513a1f2"
        )

        # Act
        create_donor_cases(mock_request)
        print(mock_create_donor_case_for_user.call_args_list)

        # Assert
        mock_create_donor_case_for_user.assert_called_once()
        called_arg = mock_create_donor_case_for_user.call_args[0][0]
        print(vars(called_arg))
        assert called_arg.user == "sarah"
        assert called_arg.guid == "25615bf2-f331-47ba-9d05-6659a513a1f2"
        assert called_arg.questionnaire_name == "LMS2309_GO1"
        assert called_arg.data_fields["cmA_ForWhom"] == "sarah"

    @mock.patch("services.blaise_service.BlaiseService.get_all_existing_donor_cases")
    @mock.patch("appconfig.config.Config.from_env") 
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch.object(blaise_restapi.Client, "get_users")
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    @mock.patch.object(blaise_restapi.Client, "create_multikey_case")
    def test_create_donor_case_is_called_the_correct_number_of_times_with_the_correct_information_when_mocking_the_blaise_service(
        self,
        mock_create_multikey_case,
        mock_get_questionnaire_data,
        mock_get_users,
        mock_questionnaire_exists_on_server_park,
        mock_get_questionnaire_for_server_park,
        mock_config_from_env,
        mock_get_all_existing_donor_cases,
    ):
        # Arrange
        mock_questionnaire_exists_on_server_park.return_value = True

        mock_config_from_env.return_value = Config(
        blaise_api_url="http://mock-url",
        blaise_server_park="gusty",
        )
        
        mock_get_all_existing_donor_cases.return_value = ["sarah"]
        mock_donor_case_model = DonorCaseModel(
            "sarah", "LMS2309_GO1", "25615bf2-f331-47ba-9d05-6659a513a1f2"
        )

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
                "role": "IPS Manager",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "IPS Manager",
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
        mock_create_multikey_case.assert_called_with(
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
                "cmA_EndDate": "29-02-2024",
                "cmA_ContactData": "MainSurveyID\t25615bf2-f331-47ba-9d05-6659a513a1f2\tID\trich\tCaseNote\tThis is the Donor Case. Select the add case button to spawn a new case with an empty shift. \tcaseinfo.Year\t2024\tcaseinfo.Survey\tIPS\tcaseinfo.Month\tFebruary\tcaseinfo.ShiftNo\t\tcaseinfo.IOut\t",
            },
        )

    @pytest.mark.parametrize(
        "questionnaire_name, role",
        [
            (None, ""),
            (None, None),
            ("", ""),
            ("", None),
        ],
    )
    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_create_donor_case_returns_message_and_400_status_code_when_both_questionnaire_name_and_role_values_are_missing(
        self, mock_get_users, questionnaire_name, role, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "role": role}
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = (
            "Error creating IPS donor cases: "
            "Missing required values from request: ['questionnaire_name', 'role']"
        )
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "questionnaire_name",
        [None, ""],
    )
    def test_create_donor_case_returns_message_and_400_status_code_when_questionnaire_name_value_is_missing(
        self, questionnaire_name, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "role": "IPS Manager"}
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: Missing required values from request: ['questionnaire_name']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "role",
        [None, ""],
    )
    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_create_donor_case_returns_message_and_400_status_code_when_role_value_is_missing(
        self, mock_get_users, role, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2306a", "role": role}
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: Missing required values from request: ['role']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_create_donor_case_returns_message_and_400_status_code_when_the_request_is_not_json(
        self, mock_get_users, caplog
    ):
        # Arrange
        mock_request = None

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = (
            "Error creating IPS donor cases: "
            "Exception raised in validate_request_is_json(). "
            "Error getting json from request 'None': 'NoneType' object has no attribute 'get_json'"
        )
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainCreateDonorCasesHandleConfigStep:
    @pytest.mark.parametrize(
        "blaise_api_url, blaise_server_park",
        [
            (None, None),
            ("", None),
            (None, ""),
            ("", ""),
        ],
    )
    @mock.patch("appconfig.config.Config.from_env")
    def test_create_donor_case_returns_message_and_400_status_code_when_both_configs_are_missing(
        self, mock_config, blaise_api_url, blaise_server_park, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url=blaise_api_url, blaise_server_park=blaise_server_park
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = (
            "Error creating IPS donor cases: "
            "Missing required values from config: ['blaise_api_url', 'blaise_server_park']"
        )
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_server_park",
        [None, ""],
    )
    @mock.patch("appconfig.config.Config.from_env")
    def test_create_donor_case_returns_message_and_400_status_code_when_blaise_server_park_config_is_missing(
        self, mock_config, blaise_server_park, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park=blaise_server_park
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: Missing required values from config: ['blaise_server_park']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_api_url",
        [None, ""],
    )
    @mock.patch("appconfig.config.Config.from_env")
    def test_create_donor_case_returns_message_and_400_status_code_when_blaise_api_url_config_is_missing(
        self, mock_config, blaise_api_url, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url=blaise_api_url, blaise_server_park="bar"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: Missing required values from config: ['blaise_api_url']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainCreateDonorCasesHandleGuidStep:

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
    def test_create_donor_case_returns_message_and_404_status_code_when_rest_api_fails_to_return_questionnaire(
        self,
        mock_rest_api_client_get_questionnaire,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_rest_api_client_get_questionnaire.side_effect = BlaiseError(
            "How do you click a button without clicking a button?"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = (
            "Error creating IPS donor cases: "
            "Exception caught in get_questionnaire(). "
            "Error getting questionnaire 'IPS2402a': How do you click a button without clicking a button?"
        )
        assert result == (error_message, 404)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    def test_create_donor_case_returns_message_and_500_status_code_when_the_guid_service_raises_an_exception(
        self,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.side_effect = GuidError(
            "Something bad happened, but I'm not telling you what"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: Something bad happened, but I'm not telling you what"
        assert result == (error_message, 500)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainCreateDonorCasesHandleUsersStep:
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    @mock.patch("services.user_service.UserService.get_users_by_role")
    def test_create_donor_case_returns_message_and_404_status_code_when_the_get_users_service_raises_a_blaise_error_exception(
        self,
        mock_get_users,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.return_value = "m0ck-gu!d"
        mock_get_users.side_effect = BlaiseError("There is butter in the ports")

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: There is butter in the ports"
        assert result == (error_message, 404)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    @mock.patch("services.user_service.UserService.get_users_by_role")
    def test_create_donor_case_returns_message_and_500_status_code_when_the_get_users_service_raises_a_users_error_exception(
        self,
        mock_get_users,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.return_value = "m0ck-gu!d"
        mock_get_users.side_effect = UsersError("Fuzion Tattoo is at it again")

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: Fuzion Tattoo is at it again"
        assert result == (error_message, 500)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    @mock.patch("services.user_service.UserService.get_users_by_role")
    def test_create_donor_case_returns_message_and_422_status_code_when_the_get_users_service_raises_a_no_users_found_with_role_exception(
        self,
        mock_get_users,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.return_value = "m0ck-gu!d"
        mock_get_users.side_effect = UsersWithRoleNotFound(
            "I've seriously run out of error messages"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = (
            "Error creating IPS donor cases: I've seriously run out of error messages"
        )
        assert result == (error_message, 422)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainCreateDonorCasesHandleDonorCasesStep:
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    @mock.patch("services.user_service.UserService.get_users_by_role")
    @mock.patch(
        "services.donor_case_service.DonorCaseService.check_and_create_donor_case_for_users"
    )
    def test_create_donor_case_returns_message_and_500_status_code_when_the_check_and_create_donor_case_for_users_service_raises_an_exception(
        self,
        mock_create_donor_case_for_users,
        mock_get_users,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.return_value = "m0ck-gu!d"
        mock_get_users.return_value = [
            {
                "name": "rich",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "IPS Manager",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]
        mock_create_donor_case_for_users.side_effect = DonorCaseError(
            "This thing unexpectedly successfully failed"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: This thing unexpectedly successfully failed"
        assert result == (error_message, 500)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainReissueNewDonorCaseFunction:
    @mock.patch("services.blaise_service.BlaiseService.get_questionnaire")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    @mock.patch(
        "services.blaise_service.BlaiseService.get_existing_donor_cases_for_user"
    )
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("blaise_restapi.Client")
    def test_reissue_new_donor_case_returns_done_and_200_status_code_for_valid_request(
        self,
        mock_client,
        mock_config,
        mock_get_existing_donor_cases_for_user,
        mock_get_users,
        mock_get_questionnaire,
    ):
        # Arrange
        mock_config.return_value = Config(
            blaise_api_url="mock-blaise-api-url", blaise_server_park="gusty"
        )

        mock_client_instance = mock.Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.questionnaire_exists_on_server_park.return_value = True

        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
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
            {
                "name": "test-user",
                "role": "IPS Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]
        mock_get_existing_donor_cases_for_user.return_value = [
            {"id": "rich", "cmA_ForWhom": "rich"}
        ]

        # Act
        response, status = reissue_new_donor_case(mock_request)

        # Assert
        assert response == "Successfully reissued new donor case for user: test-user"
        assert status == 200


class TestMainReissueNewDonorCasesHandleRequestStep:

    @mock.patch("services.validation_service.ValidationService.validate_config", return_value=None)
    @mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases_for_user")
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("services.blaise_service.BlaiseService.get_questionnaire")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    @mock.patch("services.blaise_service.BlaiseService.get_all_existing_donor_cases")
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    @mock.patch("services.validation_service.ValidationService.validate_questionnaire_exists")
    def test_reissue_new_donor_case_is_called_the_correct_number_of_times_with_the_correct_information(
        self,
        mock_validate_questionnaire_exists, 
        mock_create_donor_case_for_user,
        mock_get_all_existing_donor_cases,
        mock_get_users,
        mock_get_questionnaire,
        mock_config,
        mock_get_existing_donor_cases_for_user,
        mock_validate_config,
    ):
        # Arrange
        mock_config.return_value = Config(
            blaise_api_url="http://mock-blaise-api-url", blaise_server_park="gusty"
        )

        mock_request = flask.Request.from_values(
        json={"questionnaire_name": "IPS2402a", "user": "rich"}
        )

        mock_get_questionnaire.return_value = {
            "name": "IPS2402a",
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
        
        mock_get_existing_donor_cases_for_user.return_value = [
        {
            "mainSurveyID": "25615bf2-f331-47ba-9d05-6659a513a1f2",
            "cmA_IsDonorCase": "1",
            "id": "rich_CASE001",
        }]

        # Act
        reissue_new_donor_case(mock_request)

        # Assert
        mock_create_donor_case_for_user.assert_called_once()
        called_model = mock_create_donor_case_for_user.call_args[0][0]
        
        assert called_model.user == "rich"
        assert called_model.questionnaire_name == "IPS2402a"
        assert called_model.guid == "25615bf2-f331-47ba-9d05-6659a513a1f2"
    
    @mock.patch("services.validation_service.ValidationService.validate_questionnaire_exists")
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
    @mock.patch.object(blaise_restapi.Client, "get_users")
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    @mock.patch.object(blaise_restapi.Client, "create_multikey_case")
    def test_reissue_new_donor_case_is_called_the_correct_number_of_times_with_the_correct_information_when_mocking_the_blaise_service(
        self,
        mock_create_multikey_case,
        mock_get_questionnaire_data,
        mock_get_users,
        mock_get_questionnaire_for_server_park,
        mock_config,
        mock_validate_questionnaire_exists,
    ):
        # Arrange
        mock_config.return_value = Config(
            blaise_api_url="http://mock-blaise-api-url", blaise_server_park="gusty"
        )

        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "rich"}
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

        mock_donor_case_model = DonorCaseModel(
            "rich", "IPS2302a", "25615bf2-f331-47ba-9d05-6659a513a1f2"
        )

        # Act
        reissue_new_donor_case(mock_request)

        # Assert
        mock_create_multikey_case.assert_called_with(
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

    @pytest.mark.parametrize(
        "questionnaire_name, user",
        [
            (None, ""),
            (None, None),
            ("", ""),
            ("", None),
        ],
    )
    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_reissue_new_donor_case_returns_message_and_400_status_code_when_both_questionnaire_name_and_user_values_are_missing(
        self, mock_get_users, questionnaire_name, user, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "user": user}
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = (
            "Error reissuing IPS donor cases: "
            "Missing required values from request: ['questionnaire_name', 'user']"
        )
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "questionnaire_name",
        [None, ""],
    )
    def test_reissue_new_donor_case_returns_message_and_400_status_code_when_questionnaire_name_value_is_missing(
        self, questionnaire_name, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": questionnaire_name, "user": "test-user"}
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: Missing required values from request: ['questionnaire_name']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "user",
        [None, ""],
    )
    def test_reissue_new_donor_case_returns_message_and_400_status_code_when_role_value_is_missing(
        self, user, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2306a", "user": user}
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: Missing required values from request: ['user']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_reissue_new_donor_case_returns_message_and_400_status_code_when_the_request_is_not_json(
        self, mock_get_users, caplog
    ):
        # Arrange
        mock_request = None

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = (
            "Error reissuing IPS donor cases: "
            "Exception raised in validate_request_is_json(). "
            "Error getting json from request 'None': 'NoneType' object has no attribute 'get_json'"
        )
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainReissueNewDonorCasesHandleConfigStep:
    @pytest.mark.parametrize(
        "blaise_api_url, blaise_server_park",
        [
            (None, None),
            ("", None),
            (None, ""),
            ("", ""),
        ],
    )
    @mock.patch("appconfig.config.Config.from_env")
    def test_reissue_new_donor_case_returns_message_and_400_status_code_when_both_configs_are_missing(
        self, mock_config, blaise_api_url, blaise_server_park, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
        )
        mock_config.return_value = Config(
            blaise_api_url=blaise_api_url, blaise_server_park=blaise_server_park
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = (
            "Error reissuing IPS donor cases: "
            "Missing required values from config: ['blaise_api_url', 'blaise_server_park']"
        )
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_server_park",
        [None, ""],
    )
    @mock.patch("appconfig.config.Config.from_env")
    def test_reissue_new_donor_case_returns_message_and_400_status_code_when_blaise_server_park_config_is_missing(
        self, mock_config, blaise_server_park, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park=blaise_server_park
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: Missing required values from config: ['blaise_server_park']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "blaise_api_url",
        [None, ""],
    )
    @mock.patch("appconfig.config.Config.from_env")
    def test_reissue_new_donor_case_returns_message_and_400_status_code_when_blaise_api_url_config_is_missing(
        self, mock_config, blaise_api_url, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
        )
        mock_config.return_value = Config(
            blaise_api_url=blaise_api_url, blaise_server_park="bar"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: Missing required values from config: ['blaise_api_url']"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainReissueNewDonorCasesHandleGuidStep:

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
    def test_reissue_new_donor_case_returns_message_and_404_status_code_when_rest_api_fails_to_return_questionnaire(
        self,
        mock_rest_api_client_get_questionnaire,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_rest_api_client_get_questionnaire.side_effect = BlaiseError(
            "How do you click a button without clicking a button?"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = (
            "Error reissuing IPS donor cases: "
            "Exception caught in get_questionnaire(). "
            "Error getting questionnaire 'IPS2402a': How do you click a button without clicking a button?"
        )
        assert result == (error_message, 404)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    def test_reissue_new_donor_case_returns_message_and_500_status_code_when_the_guid_service_raises_an_exception(
        self,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.side_effect = GuidError(
            "Something bad happened, but I'm not telling you what"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: Something bad happened, but I'm not telling you what"
        assert result == (error_message, 500)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainReissueNewDonorCasesHandleUsersStep:
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    @mock.patch("services.user_service.UserService.get_user_by_name")
    def test_reissue_new_donor_case_returns_message_and_404_status_code_when_the_get_user_by_name_raises_a_blaise_error_exception(
        self,
        mock_get_user_by_name,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.return_value = "m0ck-gu!d"
        mock_get_user_by_name.side_effect = BlaiseError("There is butter in the ports")

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: There is butter in the ports"
        assert result == (error_message, 404)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch("services.guid_service.GUIDService.get_guid")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    def test_reissue_new_donor_case_raises_an_exception_and_returns_message_and_500_status_code_when_specified_user_is_not_found(
        self,
        mock_get_users,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "random-nonexistent-user"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.return_value = "m0ck-gu!d"
        mock_get_users.return_value = [
            {
                "name": "rich",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "IPS Manager",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: Exception caught in get_user_by_name(). Error getting user by username for server park bar: User random-nonexistent-user not found in server park bar"
        assert result == (error_message, 500)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainReissueNewDonorCasesHandleDonorCasesStep:
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    @mock.patch(
        "services.blaise_service.BlaiseService.get_existing_donor_cases_for_user"
    )
    @mock.patch("services.guid_service.GUIDService.get_guid")
    @mock.patch("services.user_service.UserService.get_user_by_name")
    @mock.patch(
        "services.donor_case_service.DonorCaseService.reissue_new_donor_case_for_user"
    )
    def test_reissue_new_donor_case_returns_message_and_500_status_code_when_the_reissue_new_donor_case_for_user_raises_an_exception(
        self,
        mock_reissue_new_donor_case_for_user,
        mock_get_existing_donor_cases_for_user,
        mock_get_users,
        mock_get_guid,
        mock_questionnaire_exists_on_server_park,
        mock_config,
        caplog,
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "user": "test-user"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_questionnaire_exists_on_server_park.return_value = True
        mock_get_guid.return_value = "m0ck-gu!d"
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
            {
                "name": "test-user",
                "role": "IPS Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]
        mock_get_existing_donor_cases_for_user.return_value = ["test-user"]
        mock_reissue_new_donor_case_for_user.side_effect = DonorCaseError(
            "This thing unexpectedly successfully failed"
        )

        # Act
        with caplog.at_level(logging.ERROR):
            result = reissue_new_donor_case(mock_request)

        # Assert
        error_message = "Error reissuing IPS donor cases: This thing unexpectedly successfully failed"

        assert result == (error_message, 500)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainGetUsersByRoleHandleRequestStep:
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    def test_get_users_by_role_is_called_the_correct_number_of_times_with_the_correct_information_ips_field_interviewers(
        self,
        mock_get_users,
        mock_config,
    ):
        # Arrange
        mock_request = flask.Request.from_values(json={"role": "IPS Field Interviewer"})

        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )

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
            {
                "name": "billy",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]

        # Act
        result = get_users_by_role(mock_request)

        # Assert
        assert mock_get_users.assert_called_with(mock_request)
        assert len(result) == 2
        assert len(result[0]) == 1
        assert result[0][0] == "billy"
        assert result[1] == 200

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    def test_get_users_by_role_is_called_the_correct_number_of_times_with_the_correct_information_ips_managers(
        self,
        mock_get_users,
        mock_config,
    ):
        # Arrange
        mock_request = flask.Request.from_values(json={"role": "IPS Manager"})

        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )

        mock_get_users.return_value = [
            {
                "name": "rich",
                "role": "IPS Manager",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "timmy",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "DST",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "billy",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]

        # Act
        result = get_users_by_role(mock_request)

        # Assert
        assert mock_get_users.assert_called_with(mock_request)
        assert len(result) == 2
        assert len(result[0]) == 1
        assert result[0][0] == "rich"
        assert result[1] == 200

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    def test_get_users_by_role_is_called_the_correct_number_of_times_with_the_correct_information_ips_pilot_interviewers(
        self,
        mock_get_users,
        mock_config,
    ):
        # Arrange
        mock_request = flask.Request.from_values(json={"role": "IPS Pilot Interviewer"})

        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )

        mock_get_users.return_value = [
            {
                "name": "rich",
                "role": "IPS Manager",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "timmy",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "jean",
                "role": "IPS Pilot Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "DST",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "billy",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]

        # Act
        result = get_users_by_role(mock_request)

        # Assert
        assert mock_get_users.assert_called_with(mock_request)
        assert len(result) == 2
        assert len(result[0]) == 1
        assert result[0][0] == "jean"
        assert result[1] == 200

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    def test_get_users_by_role_is_called_the_correct_number_of_times_with_the_incorrect_information(
        self,
        mock_get_users,
        mock_config,
    ):
        # Arrange
        mock_request = flask.Request.from_values(json={"role": "Made Up Role"})

        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )

        mock_get_users.return_value = [
            {
                "name": "rich",
                "role": "IPS Manager",
                "serverParks": ["gusty", "cma"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "timmy",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "jean",
                "role": "IPS Pilot Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "DST",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "billy",
                "role": "IPS Field Interviewer",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]

        # Act
        result = get_users_by_role(mock_request)

        # Assert
        assert mock_get_users.assert_called_with(mock_request)
        assert len(result) == 2
        assert len(result[0]) == 1
        assert (
            result[0][0]
            == "Error retrieving users: Made Up Role is not a valid role. Please choose one of the following roles: ['IPS Manager', 'IPS Field Interviewer', 'IPS Pilot Interviewer']"
        )
        assert result[1] == 400

    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    def test_get_users_by_role_is_called_the_correct_number_of_times_with_the_correct_information_ips_pilot_interviewers_no_users(
        self,
        mock_get_users,
        mock_config,
    ):
        # Arrange
        mock_request = flask.Request.from_values(json={"role": "IPS Pilot Interviewer"})

        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )

        mock_get_users.return_value = [
            {
                "name": "timmy",
                "role": "DST",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "jean",
                "role": "BDSS",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "sarah",
                "role": "DST",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
            {
                "name": "billy",
                "role": "DST",
                "serverParks": ["gusty"],
                "defaultServerPark": "gusty",
            },
        ]

        # Act
        result = get_users_by_role(mock_request)

        # Assert
        assert mock_get_users.assert_called_with(mock_request)
        assert len(result) == 2
        assert len(result[0]) == 0
        assert result[1] == 200
