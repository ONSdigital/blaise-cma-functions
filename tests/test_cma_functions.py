from functions import cma_functions
from tests.helpers import mock_get_users

def test_filter_users_returns_a_list_of_ips_field_interviewers_():
    # Arrange
    users = mock_get_users("IPS Field Interviewer")

    # Act
    result = cma_functions.get_ips_field_interviewers(users, "IPS Field Interviewer")

    # Assert
    assert len(result) == 1
    assert result == ["willij"]

def test_filter_users_returns_empty_list_when_no_ips_field_interviewers():
    # Arrange
    users = mock_get_users("DST")

    # Act
    result = cma_functions.get_ips_field_interviewers(users, "IPS Field Interviewer")

    # Assert
    assert len(result) == 0
    assert result == []
