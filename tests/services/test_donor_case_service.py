import logging
import pytest

from unittest import mock

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from tests.helpers import get_default_config
from utilities.custom_exceptions import DonorCaseError


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@pytest.fixture()
def donor_case_service(blaise_service) -> DonorCaseService:
    return DonorCaseService(blaise_service=blaise_service)


class TestDonorCaseDoesNotExist:
    def test_donor_case_does_not_exist_returns_false_if_donor_case_exists(
            self, donor_case_service
    ):
        # Act
        user = "rich"
        users_with_existing_donor_cases = ["rich", "sarah"]

        # Arrange
        result = donor_case_service.donor_case_does_not_exist(
            user, users_with_existing_donor_cases
        )

        # Assert
        assert result is False

    def test_donor_case_does_not_exist_returns_true_if_donor_case_does_not_exist(
        self, donor_case_service
    ):
        # Act
        user = "james"
        users_with_existing_donor_cases = ["rich", "sarah"]

        # Arrange
        result = donor_case_service.donor_case_does_not_exist(
            user, users_with_existing_donor_cases
        )

        # Assert
        assert result is True

    def test_donor_case_does_not_exist_returns_true_if_an_empty_list_is_provided(
        self, donor_case_service
    ):
        # Act
        user = "james"
        users_with_existing_donor_cases = []

        # Arrange
        result = donor_case_service.donor_case_does_not_exist(
            user, users_with_existing_donor_cases
        )

        # Assert
        assert result is True

    def test_donor_case_exists_logs_correct_information_when_case_exists(
        self, donor_case_service, caplog
    ):
        # Act
        user = "rich"
        users_with_existing_donor_cases = ["rich", "sarah"]

        # Arrange
        with caplog.at_level(logging.INFO):
            donor_case_service.donor_case_does_not_exist(
                user, users_with_existing_donor_cases
            )

        # Assert
        assert (
            "root",
            logging.INFO,
            "Donor case already exists for user 'rich'",
        ) in caplog.record_tuples

    def test_donor_case_exists_logs_correct_information_when_case_does_not_exist(
        self, donor_case_service, caplog
    ):
        # Act
        user = "james"
        users_with_existing_donor_cases = ["rich", "sarah"]

        # Arrange
        with caplog.at_level(logging.INFO):
            donor_case_service.donor_case_does_not_exist(
                user, users_with_existing_donor_cases
            )

        # Assert
        assert (
            "root",
            logging.INFO,
            "Donor case does not exist for user 'james'",
        ) in caplog.record_tuples

    def test_donor_case_exists_logs_an_error_message(
        self, donor_case_service, caplog
    ):
        # Act
        user = "james"
        users_with_existing_donor_cases = None

        # Arrange
        with caplog.at_level(logging.INFO):
            donor_case_service.donor_case_does_not_exist(
                user, users_with_existing_donor_cases
            )

        # Assert
        assert (
            "root",
            40,
            "Error checking donor case exists for james: argument of type 'NoneType' is not iterable",
        ) in caplog.record_tuples


class TestCheckAndCreateDonorCaseForUsers:
    @mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases")
    def test_check_and_create_donor_case_for_users_raises_donor_case_error_exception_when_get_existing_donor_cases_fails(
            self, mock_get_existing_donor_cases, donor_case_service, caplog):
        # arrange
        mock_get_existing_donor_cases.side_effect = Exception("You sat in Sheldon's spot")
        questionnaire_name = "foo"
        guid = "bar"
        users_with_role = ["foobar"]

        # act
        with pytest.raises(DonorCaseError) as err:
            donor_case_service.check_and_create_donor_case_for_users(
                questionnaire_name, guid, users_with_role
            )

        # assert
        error_message = (
            "Error when checking and creating donor cases: You sat in Sheldon's spot"
        )
        assert err.value.args[0] == error_message
        assert (
                   "root",
                   logging.ERROR,
                   error_message,
               ) in caplog.record_tuples
