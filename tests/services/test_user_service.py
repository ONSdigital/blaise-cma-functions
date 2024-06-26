from unittest import mock

import pytest

from appconfig.config import Config
from services.blaise_service import BlaiseService
from services.user_service import UserService
from tests.helpers import get_default_config
from utilities.custom_exceptions import BlaiseError


@pytest.fixture()
def config() -> Config:
    return get_default_config()


@pytest.fixture()
def blaise_service(config) -> BlaiseService:
    return BlaiseService(config=config)


@pytest.fixture()
def user_service(blaise_service) -> UserService:
    return UserService(blaise_service=blaise_service)


@mock.patch.object(BlaiseService, "get_users")
def test_get_users_by_role_returns_a_list_of_users_with_a_given_role(
    get_users, user_service
):
    # Arrange
    get_users.return_value = [
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
    ]
    role = "IPS Field Interviewer"
    blaise_server_park = "gusty"

    # Act
    result = user_service.get_users_by_role(blaise_server_park, role)

    # Assert
    assert len(result) == 1
    assert result == ["rich"]


@mock.patch.object(BlaiseService, "get_users")
def test_get_users_by_role_raises_a_blaise_error_exception_when_get_users_fails_with_blaise_error(
    get_users, user_service
):
    # Arrange
    get_users.side_effect = BlaiseError(
        "All the rum has gone and Jack Sparrow doesn't understand why?"
    )
    role = "IPS Field Interviewer"
    blaise_server_park = "gusty"

    # Act
    with pytest.raises(BlaiseError) as err:
        user_service.get_users_by_role(blaise_server_park, role)

    # Assert
    error_message = "All the rum has gone and Jack Sparrow doesn't understand why?"
    assert err.value.args[0] == error_message
