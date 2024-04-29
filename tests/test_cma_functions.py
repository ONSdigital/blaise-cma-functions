from appconfig.config import Config
import pytest
from unittest.mock import Mock
from tests.helpers import get_default_config
from services.blaise_service import BlaiseService
import blaise_restapi


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


def test_get_guid_returns_the_guid_as_a_string(blaise_service, mock_get_questionnaires):
    # Act
    result = blaise_service.get_quid(mock_get_questionnaires)

    # Assert
    assert isinstance(result, str)
    assert result == "25615bf2-f331-47ba-9d05-6659a513a1f2"


# def test_get_users_by_role_returns_a_list_of_users_with_a_given_role():
#     # Arrange
#     users = mock_get_users("IPS Field Interviewer")
#
#     # Act
#     result = cma_functions.get_users_by_role(users, "IPS Field Interviewer")
#
#     # Assert
#     assert len(result) == 1
#     assert result == ["willij"]
#
#
# def test_get_users_by_role_returns_empty_list_when_no_users_are_found_with_a_given_role():
#     # Arrange
#     users = mock_get_users("DST")
#
#     # Act
#     result = cma_functions.get_users_by_role(users, "IPS Field Interviewer")
#
#     # Assert
#     assert len(result) == 0
#     assert result == []
