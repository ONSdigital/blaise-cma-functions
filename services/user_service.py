from services.blaise_service import BlaiseService


class UserService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def get_users_by_role(self, role: str) -> list[str]:
        users = self._blaise_service.get_users("gusty")
        return [user["name"] for user in users if user["role"] == role]