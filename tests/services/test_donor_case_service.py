import logging
from unittest import mock

import pytest

from appconfig.config import Config
from models.donor_case_model import DonorCaseModel
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from tests.helpers import get_default_config
from utilities.custom_exceptions import BlaiseError, DonorCaseError


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

    def test_donor_case_exists_logs_an_error_message_and_raises_a_donor_case_error_exception(
        self, donor_case_service, caplog
    ):
        # Act
        user = "james"
        users_with_existing_donor_cases = None

        # Arrange
        with pytest.raises(DonorCaseError) as err:
            donor_case_service.donor_case_does_not_exist(
                user, users_with_existing_donor_cases
            )

        # Assert
        error_message = (
            "Exception raised in donor_case_does_not_exist(). "
            "Error checking donor case exists for james: argument of type 'NoneType' is not iterable"
        )
        assert err.value.args[0] == error_message
        assert (
            "root",
            40,
            error_message,
        ) in caplog.record_tuples


class TestCheckAndCreateDonorCaseForUsers:
    @mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases")
    def test_check_and_create_donor_case_for_users_raises_blaise_error_exception_when_get_existing_donor_cases_fails_with_blaise_error(
        self, mock_get_existing_donor_cases, donor_case_service
    ):
        # arrange
        mock_get_existing_donor_cases.side_effect = BlaiseError(
            "I'm running out of error messages"
        )

        questionnaire_name = "foo"
        guid = "bar"
        users_with_role = ["foobar"]

        # act
        with pytest.raises(BlaiseError) as err:
            donor_case_service.check_and_create_donor_case_for_users(
                questionnaire_name, guid, users_with_role
            )

        # assert
        assert err.value.args[0] == "I'm running out of error messages"

    @mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases")
    @mock.patch(
        "services.donor_case_service.DonorCaseService.donor_case_does_not_exist"
    )
    def test_check_and_create_donor_case_for_users_raises_donor_case_error_exception_when_donor_case_does_not_exist_fails_with_donor_case_exception(
        self,
        mock_donor_case_does_not_exist,
        mock_get_existing_donor_cases,
        donor_case_service,
        caplog,
    ):
        # arrange
        mock_get_existing_donor_cases.return_value = ["james", "rich"]
        mock_donor_case_does_not_exist.side_effect = DonorCaseError(
            "You sat in Sheldon's spot"
        )

        questionnaire_name = "foo"
        guid = "bar"
        users_with_role = ["foobar"]

        # act
        with pytest.raises(DonorCaseError) as err:
            donor_case_service.check_and_create_donor_case_for_users(
                questionnaire_name, guid, users_with_role
            )

        # assert
        assert err.value.args[0] == "You sat in Sheldon's spot"

    @mock.patch("services.blaise_service.BlaiseService.get_existing_donor_cases")
    @mock.patch(
        "services.donor_case_service.DonorCaseService.donor_case_does_not_exist"
    )
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    def test_check_and_create_donor_case_for_users_raises_blaise_error_exception_when_create_donor_case_for_users_fails_with_blaise_error(
        self,
        mock_create_donor_case_for_user,
        mock_donor_case_does_not_exist,
        mock_get_existing_donor_cases,
        donor_case_service,
        caplog,
    ):
        # arrange
        mock_get_existing_donor_cases.return_value = ["james", "rich"]
        mock_donor_case_does_not_exist.return_value = True
        mock_create_donor_case_for_user.side_effect = BlaiseError(
            "Rich has been renaming variables"
        )

        questionnaire_name = "IPS2406a"
        guid = "7bded891-3aa6-41b2-824b-0be514018806"
        users_with_role = ["IPS Manager"]

        # act
        with pytest.raises(BlaiseError) as err:
            donor_case_service.check_and_create_donor_case_for_users(
                questionnaire_name, guid, users_with_role
            )

        # assert
        assert err.value.args[0] == "Rich has been renaming variables"


class TestReissueNewDonorCaseForUser:
    @mock.patch("services.blaise_service.BlaiseService.get_donor_cases_for_user")
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    def test_reissue_new_donor_case_for_user_creates_new_case_with_incremented_id(
        self,
        mock_create_donor_case_for_user,
        mock_get_donor_cases_for_user,
        donor_case_service,
        caplog,
    ):
        # Arrange
        questionnaire_name = "IPS2406a"
        guid = "7bded891-3aa6-41b2-824b-0be514018806"
        user = "test-user"
        mock_get_donor_cases_for_user.return_value = [
            {"id": "test-user"},
            {"id": "1-test-user"},
        ]

        # Act
        with caplog.at_level(logging.INFO):
            donor_case_service.reissue_new_donor_case_for_user(
                questionnaire_name, guid, user
            )

        # Assert
        mock_create_donor_case_for_user.assert_called_once()
        assert (
            mock_create_donor_case_for_user.call_args[0][0].data_fields["id"]
            == "2-test-user"
        )
        assert (
            "root",
            logging.INFO,
            f"New Donor case created for user {user} with ID of 2-test-user",
        ) in caplog.record_tuples

    @mock.patch("services.blaise_service.BlaiseService.get_donor_cases_for_user")
    def test_reissue_new_donor_case_for_user_raises_exception_when_no_existing_case(
        self,
        mock_get_donor_cases_for_user,
        donor_case_service,
    ):
        # Arrange
        questionnaire_name = "IPS2406a"
        guid = "7bded891-3aa6-41b2-824b-0be514018806"
        user = "test-user"
        mock_get_donor_cases_for_user.return_value = []

        # Act & Assert
        with pytest.raises(DonorCaseError) as err:
            donor_case_service.reissue_new_donor_case_for_user(
                questionnaire_name, guid, user
            )

        assert err.value.args[0] == "Exception caught in reissue_new_donor_case_for_user(). Cannot reissue a new donor case. User has no existing donor cases."

    @mock.patch("services.blaise_service.BlaiseService.get_donor_cases_for_user")
    def test_reissue_new_donor_case_for_user_raises_blaise_error_when_get_donor_cases_fails(
        self,
        mock_get_donor_cases_for_user,
        donor_case_service,
    ):
        # Arrange
        mock_get_donor_cases_for_user.side_effect = BlaiseError(
            "Failed to fetch donor cases"
        )
        questionnaire_name = "IPS2406a"
        guid = "7bded891-3aa6-41b2-824b-0be514018806"
        user = "test-user"

        # Act & Assert
        with pytest.raises(BlaiseError) as err:
            donor_case_service.reissue_new_donor_case_for_user(
                questionnaire_name, guid, user
            )

        assert err.value.args[0] == "Failed to fetch donor cases"

    @mock.patch("services.blaise_service.BlaiseService.get_donor_cases_for_user")
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    def test_reissue_new_donor_case_for_user_raises_donor_case_error_when_create_donor_case_fails(
        self,
        mock_create_donor_case_for_user,
        mock_get_donor_cases_for_user,
        donor_case_service,
    ):
        # Arrange
        mock_get_donor_cases_for_user.return_value = [{"id": "donor_case_1"}]
        mock_create_donor_case_for_user.side_effect = DonorCaseError(
            "Failed to create donor case"
        )
        questionnaire_name = "IPS2406a"
        guid = "7bded891-3aa6-41b2-824b-0be514018806"
        user = "test-user"

        # Act & Assert
        with pytest.raises(DonorCaseError) as err:
            donor_case_service.reissue_new_donor_case_for_user(
                questionnaire_name, guid, user
            )

        assert err.value.args[0] == "Failed to create donor case"

    @mock.patch("services.blaise_service.BlaiseService.get_donor_cases_for_user")
    @mock.patch("services.blaise_service.BlaiseService.create_donor_case_for_user")
    def test_reissue_new_donor_case_for_user_raises_generic_exception_when_an_unexpected_error_occurs(
        self,
        mock_create_donor_case_for_user,
        mock_get_donor_cases_for_user,
        donor_case_service,
    ):
        # Arrange
        mock_get_donor_cases_for_user.return_value = [{"id": "donor_case_1"}]
        mock_create_donor_case_for_user.side_effect = Exception(
            "Unexpected error occurred"
        )
        questionnaire_name = "IPS2406a"
        guid = "7bded891-3aa6-41b2-824b-0be514018806"
        user = "test-user"

        # Act & Assert
        with pytest.raises(DonorCaseError) as err:
            donor_case_service.reissue_new_donor_case_for_user(
                questionnaire_name, guid, user
            )

        assert (
            "Exception caught in reissue_new_donor_case_for_user(). Error when resetting donor case: Unexpected error occurred"
            in str(err.value)
        )
