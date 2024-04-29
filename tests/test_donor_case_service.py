from appconfig.config import Config
import pytest

from tests.helpers import get_default_config
from services.donor_case_service import DonorCaseService
from services.blaise_service import BlaiseService



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
