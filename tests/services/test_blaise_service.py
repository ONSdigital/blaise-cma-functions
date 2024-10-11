import logging
from unittest import mock

import blaise_restapi
import pytest

from appconfig.config import Config
from models.donor_case_model import DonorCaseModel
from services.blaise_service import BlaiseService
from tests.helpers import get_default_config
from utilities.custom_exceptions import BlaiseError
from utilities.regex import extract_username_from_case_id


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


class TestGetQuestionnaire:
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
    def test_get_questionnaire_calls_the_rest_api_endpoint_with_the_correct_parameters(
        self, _mock_rest_api_client, blaise_service
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
        self, _mock_rest_api_client_get_questionnaire_for_server_park, blaise_service
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
        result = blaise_service.get_questionnaire(
            blaise_server_park, questionnaire_name
        )

        # Assert
        assert len(result) == 9
        assert isinstance(result, dict)

        assert result["name"] == "LMS2309_GO1"
        assert result["id"] == "25615bf2-f331-47ba-9d05-6659a513a1f2"
        assert result["serverParkName"] == "gusty"

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
    def test_get_questionnaire_logs_the_correct_information(
        self,
        _mock_rest_api_client_get_questionnaire_for_server_park,
        blaise_service,
        caplog,
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

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_for_server_park")
    def test_get_questionnaire_logs_error_and_raises_blaise_questionnaire_error_exception(
        self, mock_rest_api_client_get_questionnaire, blaise_service, caplog
    ):
        # Arrange
        mock_rest_api_client_get_questionnaire.side_effect = Exception(
            "DFS had to end their sale"
        )

        blaise_server_park = "gusty"
        questionnaire_name = "LMS2309_GO1"

        # Act
        with pytest.raises(BlaiseError) as err:
            blaise_service.get_questionnaire(blaise_server_park, questionnaire_name)

        # Assert
        error_message = (
            "Exception caught in get_questionnaire(). "
            "Error getting questionnaire 'LMS2309_GO1': DFS had to end their sale"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestGetUsers:
    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_get_users_calls_the_rest_api_endpoint_with_the_correct_parameters(
        self, _mock_rest_api_client, blaise_service
    ):
        # Arrange
        blaise_server_park = "gusty"

        # Act
        blaise_service.get_users(blaise_server_park)

        # Assert
        _mock_rest_api_client.assert_called_with()

    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_get_users_returns_a_list_of_dictionaires_containing_user_info(
        self, _mock_rest_api_client_get_users, blaise_service, mock_get_users
    ):
        # Arrange
        _mock_rest_api_client_get_users.return_value = mock_get_users

        blaise_server_park = "gusty"

        # Act
        result = blaise_service.get_users(blaise_server_park)

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

    @mock.patch.object(blaise_restapi.Client, "get_users")
    def test_get_users_logs_error_and_raises_blaise_error_exception(
        self, mock_rest_api_client_get_users, blaise_service, caplog
    ):
        # Arrange
        mock_rest_api_client_get_users.side_effect = Exception(
            "No more violins left to score Bridgerton"
        )
        server_park = "foo"

        # Act
        with pytest.raises(BlaiseError) as err:
            blaise_service.get_users(server_park)

        # Assert
        error_message = (
            "Exception caught in get_users(). "
            "Error getting users from server park foo: No more violins left to score Bridgerton"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestGetExistingDonorCases:
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_all_existing_donor_cases_calls_the_rest_api_endpoint_with_the_correct_parameters(
        self, _mock_rest_api_client, blaise_service
    ):
        # Arrange
        server_park = "cma"
        questionnaire_name = "CMA_Launcher"
        field_data = ["MainSurveyID", "id", "CMA_IsDonorCase"]
        guid = "7bded891-3aa6-41b2-824b-0be514018806"
        filter = f"MainSurveyID='{guid}'"

        # Act
        blaise_service.get_all_existing_donor_cases(guid)

        # Assert
        _mock_rest_api_client.assert_called_with(
            server_park, questionnaire_name, field_data, filter
        )

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_all_existing_donor_cases_returns_a_list_of_unique_ids_(
        self, _mock_rest_api_client_get_questionnaire_data, blaise_service
    ):
        # Arrange
        _mock_rest_api_client_get_questionnaire_data.return_value = {
            "questionnaireName": "cma_launcher",
            "questionnaireId": "b0425080-2470-49db-bb53-170633c4fbba",
            "reportingData": [
                {
                    "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
                    "id": "rich",
                    "cmA_IsDonorCase": "1",
                },
                {
                    "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
                    "id": "james",
                    "cmA_IsDonorCase": "1",
                },
                {
                    "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
                    "id": "rich",
                    "cmA_IsDonorCase": "",
                },
                {
                    "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
                    "id": "james",
                    "cmA_IsDonorCase": "",
                },
            ],
        }
        guid = "7bded891-3aa6-41b2-824b-0be514018806"

        # Act
        result = blaise_service.get_all_existing_donor_cases(guid)

        # Assert
        assert len(result) == 2
        assert result == ["james", "rich"]

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_all_existing_donor_cases_returns_a_list_of_existing_donor_cases_for_the_correct_questionnaire_when_multiple_questionnaires_are_installed(
        self, _mock_rest_api_client_get_questionnaire_data, blaise_service
    ):
        # Arrange
        _mock_rest_api_client_get_questionnaire_data.return_value = {
            "questionnaireName": "cma_launcher",
            "questionnaireId": "b0425080-2470-49db-bb53-170633c4fbba",
            "reportingData": [
                {
                    "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
                    "id": "cal",
                    "cmA_IsDonorCase": "1",
                },
                {
                    "mainSurveyID": "861ecb9b-4154-4f50-9b47-7fd52c098313",
                    "id": "cal",
                    "cmA_IsDonorCase": "1",
                },
                {
                    "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
                    "id": "james",
                    "cmA_IsDonorCase": "1",
                },
                {
                    "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
                    "id": "james",
                    "cmA_IsDonorCase": "",
                },
            ],
        }
        guid = "861ecb9b-4154-4f50-9b47-7fd52c098313"

        # Act
        result = blaise_service.get_all_existing_donor_cases(guid)

        # Assert
        assert len(result) == 1
        assert result == ["cal"]

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_all_existing_donor_cases_logs_error_and_raises_exception(
        self, mock_rest_api_client_get_users, blaise_service, caplog
    ):
        # Arrange
        mock_rest_api_client_get_users.side_effect = Exception(
            "Daryl Dixon did not claim this"
        )
        guid = "7h15-i5-a-gu!D"

        # Act
        with pytest.raises(BlaiseError) as err:
            blaise_service.get_all_existing_donor_cases(guid)

        # Assert
        error_message = (
            "Exception caught in get_all_existing_donor_cases(). "
            "Error getting existing donor cases: Exception caught in get_questionnaire_cases(). "
            "Error getting questionnaire cases from server park cma: Daryl Dixon did not claim this"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestCreateDonorCaseForUser:
    @mock.patch.object(blaise_restapi.Client, "create_multikey_case")
    def test_create_donor_case_for_user_logs_an_informative_message(
        self, _mock_rest_api_client_create_multikey_case, blaise_service, caplog
    ):
        # Arrange
        donor_case_model = DonorCaseModel(
            user="Arya Stark", questionnaire_name="IPS2406a", guid="7h15-i5-a-gu!d"
        )

        # Act
        with caplog.at_level(logging.INFO):
            blaise_service.create_donor_case_for_user(donor_case_model)

        # Assert
        assert (
            "root",
            logging.INFO,
            "Created donor case for user 'Arya Stark' for questionnaire IPS2406a",
        ) in caplog.record_tuples

    @mock.patch.object(blaise_restapi.Client, "create_multikey_case")
    def test_create_donor_case_for_user_logs_error_and_raises_exception(
        self, mock_rest_api_client_create_multikey_case, blaise_service, caplog
    ):
        # Arrange
        mock_rest_api_client_create_multikey_case.side_effect = Exception(
            "John Snow be knowin'"
        )
        donor_case_model = DonorCaseModel(
            user="Arya Stark", questionnaire_name="IPS2406a", guid="7h15-i5-a-gu!d"
        )

        # Act
        with pytest.raises(BlaiseError) as err:
            blaise_service.create_donor_case_for_user(donor_case_model)

        # Assert
        error_message = (
            "Exception caught in create_donor_case_for_user(). "
            "Error creating donor case for user 'Arya Stark': John Snow be knowin'"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples


class TestGetDonorCasesForUser:
    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_existing_donor_cases_for_user_calls_rest_api_and_returns_correct_cases(
        self, mock_rest_api_client_get_questionnaire_data, blaise_service
    ):
        # Arrange
        mock_rest_api_client_get_questionnaire_data.return_value = {
            "reportingData": [
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Arya Stark",
                    "cmA_IsDonorCase": "1",
                    "id": "aryastark",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow",
                    "cmA_IsDonorCase": "",
                    "id": "jonsnow-3",
                },
                {
                    "mainSurveyID": "different-guid",
                    "id": "Jon Snow",
                    "cmA_IsDonorCase": "",
                    "id": "jonsnow-2",
                },
            ]
        }
        guid = "7h15-i5-a-gu!d"
        user = "jonsnow"

        # Act
        result = blaise_service.get_existing_donor_cases_for_user(guid, user)

        # Assert
        assert len(result) == 1
        assert extract_username_from_case_id(result[0]["id"]) == "jonsnow"
        assert result[0]["cmA_IsDonorCase"] == "1"

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_existing_donor_cases_for_user_returns_donor_cases_for_specified_user_when_the_user_has_a_similar_username_to_other_users(
        self, mock_rest_api_client_get_questionnaire_data, blaise_service
    ):
        # Arrange
        mock_rest_api_client_get_questionnaire_data.return_value = {
            "reportingData": [
                # Old donor case model ID
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow32",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow32",
                },
                # New donor case model ID
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow32",
                    "cmA_IsDonorCase": "1",
                    "id": "1-jonsnow32",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Arya Stark",
                    "cmA_IsDonorCase": "1",
                    "id": "aryastark",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow32ing",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow32ing",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snowy",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnowy",
                },
                {
                    "mainSurveyID": "different-guid",
                    "id": "Jon Snow",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow",
                },
            ]
        }
        guid = "7h15-i5-a-gu!d"
        user = "jonsnow32"

        # Act
        result = blaise_service.get_existing_donor_cases_for_user(guid, user)

        # Assert
        assert len(result) == 2
        assert extract_username_from_case_id(result[0]["id"]) == "jonsnow32"
        assert extract_username_from_case_id(result[1]["id"]) == "jonsnow32"
        assert result[0]["cmA_IsDonorCase"] == "1"
        assert result[1]["cmA_IsDonorCase"] == "1"

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_existing_donor_cases_for_user_returns_donor_cases_for_specified_user_when_the_id_begins_with_number(
        self, mock_rest_api_client_get_questionnaire_data, blaise_service
    ):
        # Arrange
        mock_rest_api_client_get_questionnaire_data.return_value = {
            "reportingData": [
                # Old donor case model ID
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow32",
                    "cmA_IsDonorCase": "1",
                    "id": "1jonsnow32",
                },
                # New donor case model ID
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow32",
                    "cmA_IsDonorCase": "1",
                    "id": "1-1jonsnow32",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Arya Stark",
                    "cmA_IsDonorCase": "1",
                    "id": "aryastark",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow32ing",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow32ing",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snowy",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnowy",
                },
                {
                    "mainSurveyID": "different-guid",
                    "id": "Jon Snow",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow",
                },
            ]
        }
        guid = "7h15-i5-a-gu!d"
        user = "1jonsnow32"

        # Act
        result = blaise_service.get_existing_donor_cases_for_user(guid, user)

        # Assert
        assert len(result) == 2
        assert extract_username_from_case_id(result[0]["id"]) == "1jonsnow32"
        assert extract_username_from_case_id(result[1]["id"]) == "1jonsnow32"
        assert result[0]["cmA_IsDonorCase"] == "1"
        assert result[1]["cmA_IsDonorCase"] == "1"

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_existing_donor_cases_for_user_returns_empty_list_when_a_specified_user_has_no_donor_case_and_has_a_similar_username_to_other_users(
        self, mock_rest_api_client_get_questionnaire_data, blaise_service
    ):
        # Arrange
        mock_rest_api_client_get_questionnaire_data.return_value = {
            "reportingData": [
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snow32",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow32",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Arya Stark",
                    "cmA_IsDonorCase": "1",
                    "id": "aryastark",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snowing",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnowing",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snowy",
                    "cmA_IsDonorCase": "",
                    "id": "jonsnowy",
                },
                {
                    "mainSurveyID": "7h15-i5-a-gu!d",
                    "id": "Jon Snowy",
                    "cmA_IsDonorCase": "",
                    "id": "1-jonsnowy",
                },
            ]
        }
        guid = "7h15-i5-a-gu!d"
        user = "jonsnow"

        # Act
        result = blaise_service.get_existing_donor_cases_for_user(guid, user)

        # Assert
        assert len(result) == 0
        assert result == []

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_existing_donor_cases_for_user_returns_empty_list_when_no_cases_found_for_a_specific_questionnaire(
        self, mock_rest_api_client_get_questionnaire_data, blaise_service
    ):
        # Arrange
        mock_rest_api_client_get_questionnaire_data.return_value = {
            "reportingData": [
                {
                    "mainSurveyID": "different-guid",
                    "id": "Jon Snow",
                    "cmA_IsDonorCase": "1",
                    "id": "jonsnow",
                },
                {
                    "mainSurveyID": "different-guid",
                    "id": "Arya Stark",
                    "cmA_IsDonorCase": "1",
                    "id": "aryastark",
                },
            ]
        }
        guid = "7h15-i5-a-gu!d"
        user = "jonsnow"

        # Act
        result = blaise_service.get_existing_donor_cases_for_user(guid, user)

        # Assert
        assert result == []

    @mock.patch.object(blaise_restapi.Client, "get_questionnaire_data")
    def test_get_existing_donor_cases_for_user_logs_error_and_raises_exception(
        self, mock_rest_api_client_get_questionnaire_data, blaise_service, caplog
    ):
        # Arrange
        mock_rest_api_client_get_questionnaire_data.side_effect = Exception(
            "The Wall has fallen"
        )

        guid = "7h15-i5-a-gu!d"
        user = "Jon Snow"

        # Act
        with pytest.raises(BlaiseError) as err:
            blaise_service.get_existing_donor_cases_for_user(guid, user)

        # Assert
        error_message = (
            "Exception caught in get_existing_donor_cases_for_user(). "
            "Error getting existing cases for user, Jon Snow: Exception caught in get_questionnaire_cases(). "
            "Error getting questionnaire cases from server park cma: The Wall has fallen"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            logging.ERROR,
            error_message,
        ) in caplog.record_tuples
