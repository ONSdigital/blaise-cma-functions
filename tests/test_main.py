from unittest import mock

from main import create_ips_donor_cases_processor


class MockRequest:
    def __init__(self, json_data):
        self.json_data = json_data

    def get_json(self):
        return self.json_data

# @mock.patch("services.user_service.UserService.get_users_by_role")
# @mock.patch("services.guid_service.GUIDService.get_guid")
# def test_create_ips_donor_cases_processor(mock_get_guid, mock_get_users_by_role):
#     # Arrange
#     mock_request = MockRequest({"questionnaire_name": "IPS2402a", "role": "IPS Manager"})
#
#     # Act
#     create_ips_donor_cases_processor(mock_request)
#
#     # Assert
#     mock_get_guid.assert_called_with("gusty", "IPS2402a")
#     mock_get_users_by_role.assert_called_with("IPS Manager")
