import logging

from services.blaise_service import BlaiseService
from utilities.custom_exceptions import BlaiseError, UsersError, UsersWithRoleNotFound
from utilities.logging import function_name


class UserService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def get_users_by_role(self, blaise_server_park: str, role: str) -> list[str]:
        try:
            blaise_users = self._blaise_service.get_users(blaise_server_park)
            ips_users = [user["name"] for user in blaise_users if user["role"] == role]
            logging.info(
                f"Got {len(ips_users)} users from server park {blaise_server_park} for role {role}"
            )
            return ips_users
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

    def get_user_by_name(self, blaise_server_park: str, username: str) -> dict:
        try:
            blaise_users = self._blaise_service.get_users(blaise_server_park)
            user = next(
                (user for user in blaise_users if user["name"] == username), None
            )
            if user:
                logging.info(
                    f"Got user {username} from server park {blaise_server_park}"
                )
                return user
            else:
                error_message = (
                    f"User {username} not found in server park {blaise_server_park}"
                )
                logging.error(error_message)
                raise UsersError(error_message)
        except BlaiseError as e:
            raise BlaiseError(e.message) from e
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error getting user by username for server park {blaise_server_park}: {e}"
            )
            logging.error(error_message)
            raise UsersError(error_message)
