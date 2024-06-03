from services.blaise_service import BlaiseService


class UserService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def get_users_by_role(self, blaise_server_park: str, role: str) -> list[str]:
        try:
            users = self._blaise_service.get_users(blaise_server_park)
            return [user["name"] for user in users if user["role"] == role]
        except Exception as e:
            raise Exception(e)
