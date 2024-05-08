import logging

from models.donor_case_model import DonorCaseModel
from services.blaise_service import BlaiseService


class DonorCaseService:
    def __init__(self, blaise_service: BlaiseService):
        self._blaise_service = blaise_service

    def create_donor_case_for_users(
        self, questionnaire_name: str, guid: str, users_with_role: list
    ) -> None:
        users_existing_donor_cases = self._blaise_service.get_existing_donor_cases()
        for user in users_with_role:
            if not self.donor_case_exists(user, users_existing_donor_cases):
                donor_case_model = DonorCaseModel(
                    user, questionnaire_name, guid
                )
                self._blaise_service.create_donor_case_for_user(donor_case_model)

    def donor_case_exists(self, user: str, users_with_existing_donor_cases) -> bool:
        try:
            if user not in users_with_existing_donor_cases:
                logging.info(f"Donor case does not exist for user '{user}'")
                return False
            else:
                logging.info(f"Donor case already exists for user '{user}'")
                return True
        except Exception as e:
            logging.error(f"Error checking donor case for user {user}: {e}")
