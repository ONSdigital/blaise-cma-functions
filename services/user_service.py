import logging

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import BlaiseError, UsersError


class UserService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def get_users_by_role(self, blaise_server_park: str, role: str) -> list[str]:
        try:
            users = self._blaise_service.get_users(blaise_server_park)
            return [user["name"] for user in users if user["role"] == role]
        except BlaiseError as e:
            error_message = (
                "BlaiseError caught in UserService.get_users_by_role(). "
                f"Error getting users by role for server park {blaise_server_park}: {e}"
            )
            logging.error(error_message)
            raise BlaiseError(error_message)
        except Exception as e:
            error_message = (
                "Generic Exception caught in UserService.get_users_by_role(). "
                f"Error getting users by role for server park {blaise_server_park}: {e}"
            )
            logging.error(error_message)
            raise UsersError(error_message)
