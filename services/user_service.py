import logging

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import BlaiseError, UsersError, UsersWithRoleNotFound
from utilities.logging import function_name


class UserService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def get_users_by_role(self, blaise_server_park: str, role: str) -> list[str]:
        try:
            users = self._blaise_service.get_users(blaise_server_park)
            return [user["name"] for user in users if user["role"] == role]
        except BlaiseError as e:
            raise BlaiseError(e.message) from e
        except UsersWithRoleNotFound as e:
            raise UsersWithRoleNotFound(e.message) from e
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting users by role for server park {blaise_server_park}: {e}"
            )
            logging.error(error_message)
            raise UsersError(error_message)
