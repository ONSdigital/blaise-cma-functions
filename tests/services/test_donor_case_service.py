import logging

import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService
from tests.helpers import get_default_config


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@pytest.fixture()
def donor_case_service(blaise_service) -> DonorCaseService:
    return DonorCaseService(blaise_service=blaise_service)


def test_donor_case_does_not_exist_returns_false_if_donor_case_exists(donor_case_service):
    # Act
    user = "rich"
    users_with_existing_donor_cases = ["rich", "sarah"]

    # Arrange
    result = donor_case_service.donor_case_does_not_exist(user, users_with_existing_donor_cases)

    # Assert
    assert result is False


def test_donor_case_does_not_exist_returns_True_if_donor_case_does_not_exist(
    donor_case_service,
):
    # Act
    user = "james"
    users_with_existing_donor_cases = ["rich", "sarah"]

    # Arrange
    result = donor_case_service.donor_case_does_not_exist(user, users_with_existing_donor_cases)

    # Assert
    assert result is True


def test_donor_case_does_not_exist_returns_true_if_an_empty_list_is_provided(
    donor_case_service,
):
    # Act
    user = "james"
    users_with_existing_donor_cases = []

    # Arrange
    result = donor_case_service.donor_case_does_not_exist(user, users_with_existing_donor_cases)

    # Assert
    assert result is True


def test_donor_case_exists_logs_correct_information_when_case_exists(
    donor_case_service, caplog
):
    # Act
    user = "rich"
    users_with_existing_donor_cases = ["rich", "sarah"]

    # Arrange
    with caplog.at_level(logging.INFO):
        donor_case_service.donor_case_does_not_exist(user, users_with_existing_donor_cases)

    # Assert
    assert (
        "root",
        logging.INFO,
        "Donor case already exists for user 'rich'",
    ) in caplog.record_tuples


def test_donor_case_exists_logs_correct_information_when_case_does_not_exist(
    donor_case_service, caplog
):
    # Act
    user = "james"
    users_with_existing_donor_cases = ["rich", "sarah"]

    # Arrange
    with caplog.at_level(logging.INFO):
        donor_case_service.donor_case_does_not_exist(user, users_with_existing_donor_cases)

    # Assert
    assert (
        "root",
        logging.INFO,
        "Donor case does not exist for user 'james'",
    ) in caplog.record_tuples


def test_donor_case_exists_logs_an_error_message(donor_case_service, caplog):
    # Act
    user = "james"
    users_with_existing_donor_cases = None

    # Arrange
    with caplog.at_level(logging.INFO):
        donor_case_service.donor_case_does_not_exist(user, users_with_existing_donor_cases)

    # Assert
    assert (
        "root",
        40,
        "Error checking donor case for user james: argument of type 'NoneType' is not iterable",
    ) in caplog.record_tuples
