from functions import cma_functions
from conftest import mock_get_users, mock_get_users_without_ips

def test_filter_users_returns_a_list_of_ips_interviewers(mock_get_users):
    result = cma_functions.filter_users(mock_get_users, "IPS Field Interviewer")

    assert len(result) == 1
    assert result == ["James"]

def test_filter_users_returns_empty_list_when_no_ips_field_interviewers_(mock_get_users_without_ips):
    result = cma_functions.filter_users(mock_get_users_without_ips, "IPS Field Interviewer")

    assert len(result) == 0
    assert result == []

test