import logging

from models.donor_case_model import DonorCaseModel
from services.blaise_service import BlaiseService
from utilities.custom_exceptions import BlaiseError, DonorCaseError
from utilities.logging import function_name


class DonorCaseService:
    def __init__(self, blaise_service: BlaiseService) -> None:
        self._blaise_service = blaise_service

    def check_and_create_donor_case_for_users(
        self, questionnaire_name: str, guid: str, users_with_role: list
    ) -> None:
        try:
            users_with_existing_donor_cases = (
                self._blaise_service.get_existing_donor_cases(guid)
            )
            for user in users_with_role:
                if self.donor_case_does_not_exist(
                    user, users_with_existing_donor_cases
                ):
                    donor_case_model = DonorCaseModel(user, questionnaire_name, guid)
                    self._blaise_service.create_donor_case_for_user(donor_case_model)
        except BlaiseError as e:
            raise BlaiseError(e.message)
        except DonorCaseError as e:
            raise DonorCaseError(e.message)
        except Exception as e:
            error_message = (
                f"Exception caught in {function_name()}. "
                f"Error when checking and creating donor cases: {e}"
            )
            logging.error(error_message)
            raise DonorCaseError(error_message)

    @staticmethod
    def donor_case_does_not_exist(
        user: str, users_with_existing_donor_cases: list[str]
    ) -> bool:
        try:
            if user in users_with_existing_donor_cases:
                logging.info(f"Donor case already exists for user '{user}'")
                return False
            elif user not in users_with_existing_donor_cases:
                logging.info(f"Donor case does not exist for user '{user}'")
                return True
        except Exception as e:
            error_message = (
                f"Exception raised in {function_name()}. "
                f"Error checking donor case exists for {user}: {e}"
            )
            logging.error(error_message)
            raise DonorCaseError(error_message)
