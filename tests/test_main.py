import logging
from unittest import mock

import blaise_restapi
import flask
import pytest

from appconfig.config import Config
from main import create_donor_cases, get_request_values
from models.donor_case_model import DonorCaseModel
from utilities.custom_exceptions import (
    BlaiseError,
    DonorCaseError,
    GuidError,
    QuestionnaireNotFound,
    UsersError,
    UsersWithRoleNotFound,
)


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    def get_json(self):
        return self.json_data


class TestMainCreateDonorCasesHandleRequestStep:

    @mock.patch("services.blaise_service.BlaiseService.get_questionnaire")
    @mock.patch("services.blaise_service.BlaiseService.get_users")
    @mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases")
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    def test_create_donor_case_is_called_the_correct_number_of_times_with_the_correct_information(
        self,
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
        self,
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

    @pytest.mark.parametrize(
        "questionnaire_name",
        [None, ""],
    )
    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_create_donor_case_returns_message_and_400_status_code_when_questionnaire_name_value_is_missing(
        self, mock_get_users, questionnaire_name, caplog
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
        error_message = "Error creating IPS donor cases: 'NoneType' object has no attribute 'get_json'"
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
            "The following environment variables are not set: blaise_api_url, blaise_server_park"
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
        error_message = "Error creating IPS donor cases: The following environment variables are not set: blaise_server_park"
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
        error_message = "Error creating IPS donor cases: The following environment variables are not set: blaise_api_url"
        assert result == (error_message, 400)
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestMainCreateDonorCasesHandleBlaiseStep:
    @mock.patch("appconfig.config.Config.from_env")
    @mock.patch.object(blaise_restapi.Client, "questionnaire_exists_on_server_park")
    def test_create_donor_case_returns_message_and_404_status_code_when_rest_api_fails_to_return_questionnaire(
        self, mock_rest_api_questionnaire_exists_on_server_park, mock_config, caplog
    ):
        # Arrange
        mock_request = flask.Request.from_values(
            json={"questionnaire_name": "IPS2402a", "role": "IPS Manager"}
        )
        mock_config.return_value = Config(
            blaise_api_url="foo", blaise_server_park="bar"
        )
        mock_rest_api_questionnaire_exists_on_server_park.return_value = False

        # Act
        with caplog.at_level(logging.ERROR):
            result = create_donor_cases(mock_request)

        # Assert
        error_message = "Error creating IPS donor cases: Questionnaire IPS2402a is not installed in Blaise"
        assert result == (error_message, 422)
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
            "Exception caught in BlaiseService.get_questionnaire(). "
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


class TestGetRequestValues:
    def test_get_request_values_returns_the_questionnaire_name_and_role(self):
        # Arrange
        mock_request = {"questionnaire_name": "IPS2402a", "role": "IPS Manager"}

        # Act
        result = get_request_values(mock_request)

        # Assert
        assert result[0] == "IPS2402a"
        assert result[1] == "IPS Manager"
        assert result == ("IPS2402a", "IPS Manager")
        assert result != ("IPS Manager", "IPS2402a")

    @pytest.mark.parametrize(
        "questionnaire_name, role",
        [
            (None, None),
            ("", None),
            (None, ""),
            ("", ""),
        ],
    )
    def test_get_request_values_logs_and_raises_value_error_exception_when_values_are_missing(
        self, questionnaire_name, role, caplog
    ):
        # Arrange
        mock_request = {"questionnaire_name": questionnaire_name, "role": role}

        # Act
        with pytest.raises(ValueError) as err:
            get_request_values(mock_request)

        # Assert
        error_message = (
            "Missing required values from request: ['questionnaire_name', 'role']"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "questionnaire_name",
        [None, ""],
    )
    def test_get_request_values_logs_and_raises_value_error_exception_when_questionnaire_name_is_missing(
        self, questionnaire_name, caplog
    ):
        # Arrange
        mock_request = {"questionnaire_name": questionnaire_name, "role": "IPS Manager"}

        # Act
        with pytest.raises(ValueError) as err:
            get_request_values(mock_request)

        # Assert
        error_message = "Missing required values from request: ['questionnaire_name']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples

    @pytest.mark.parametrize(
        "role",
        [None, ""],
    )
    def test_get_request_values_logs_and_raises_value_error_exception_when_role_is_missing(
        self, role, caplog
    ):
        # Arrange
        mock_request = {"questionnaire_name": "IPS2402a", "role": role}

        # Act
        with pytest.raises(ValueError) as err:
            get_request_values(mock_request)

        # Assert
        error_message = "Missing required values from request: ['role']"
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples
