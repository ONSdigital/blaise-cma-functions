from appconfig.config import Config
import pytest

from tests.helpers import get_default_config
from services.donor_case_service import DonorCaseService
from services.blaise_service import BlaiseService

import logging


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@pytest.fixture()
def donor_case_service(blaise_service) -> DonorCaseService:
    return DonorCaseService(blaise_service=blaise_service)


def test_donor_case_exists_returns_true_if_donor_case_exists(donor_case_service):
    user = "rich"
    users_with_existing_donor_cases = ["rich", "sarah"]

    result = donor_case_service.donor_case_exists(user, users_with_existing_donor_cases)

    assert result is True


def test_donor_case_exists_returns_false_if_donor_case_does_not_exist(donor_case_service):
    user = "rich"
    users_with_existing_donor_cases = ["james", "sarah"]

    result = donor_case_service.donor_case_exists(user, users_with_existing_donor_cases)

    assert result is False


def test_donor_case_exists_logs_correct_information_when_case_exists(donor_case_service, caplog):
    user = "rich"
    users_with_existing_donor_cases = ["rich", "sarah"]

    with caplog.at_level(logging.INFO): donor_case_service.donor_case_exists(user, users_with_existing_donor_cases)

    assert (
               "root",
               logging.INFO,
               "Donor case already exists for user 'rich'",
           ) in caplog.record_tuples


def test_donor_case_exists_logs_correct_information_when_case_does_not_exist(donor_case_service, caplog):
    user = "james"
    users_with_existing_donor_cases = ["rich", "sarah"]

    with caplog.at_level(logging.INFO): donor_case_service.donor_case_exists(user, users_with_existing_donor_cases)

    assert (
               "root",
               logging.INFO,
               "Donor case does not exist for user 'james'",
           ) in caplog.record_tuples


def test_donor_case_exists_logs_an_error_message(donor_case_service, caplog):
    user = "james"
    users_with_existing_donor_cases = None

    with caplog.at_level(logging.INFO): donor_case_service.donor_case_exists(user, users_with_existing_donor_cases)

    assert (
               "root",
               40,
               "Error checking donor case for user james: argument of type 'NoneType' is not iterable",
           ) in caplog.record_tuples
