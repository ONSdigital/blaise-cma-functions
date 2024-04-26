from services.cma_service import CMAService
from tests.helpers import mock_get_users

import logging
from unittest.mock import patch


def test_get_guid_returns_the_guid_as_a_string(mock_get_guestionnaires):
    # Act
    result = CMAService.get_quid(mock_get_guestionnaires)

    # Assert
    assert isinstance(result, str)
    assert result == "25615bf2-f331-47ba-9d05-6659a513a1f2"
#
#
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
