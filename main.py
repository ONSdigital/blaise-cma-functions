import logging
from services.blaise_service import CMAService


def create_ips_donor_cases_processer(request):
    logging.info("Running Cloud Function - create_ips_donor_cases")
    cma_service = CMAService()

    request_json = request.get_json()
    questionnaire_name = request_json["questionnaire_name"]
    role = request_json["role"]

    questionnaire = cma_service.get_questionnaire("gusty", questionnaire_name)
    guid = cma_service.get_quid("gusty", questionnaire)

    users = cma_service.get_users("gusty")
    users_with_role = cma_service.get_users_by_role(role)

    cma_service.create_donor_cases(questionnaire_name, guid, users_with_role)

    return "Done!", 200
