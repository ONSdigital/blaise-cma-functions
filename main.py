import logging

from services.blaise_service import BlaiseService
from services.donor_case_service import DonorCaseService


def create_ips_donor_cases_processor(request):
    logging.info("Running Cloud Function - create_ips_donor_cases")
    blaise_service = BlaiseService()

    request_json = request.get_json()
    questionnaire_name = request_json["questionnaire_name"]
    role = request_json["role"]

    guid = blaise_service.get_quid("gusty", questionnaire_name)
    users_with_role = blaise_service.get_users_by_role(role)
    DonorCaseService.create_donor_case_for_users(
        questionnaire_name, guid, users_with_role
    )
    return "Done!", 200
