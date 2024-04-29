import logging
from services.blaise_service import BlaiseService


def create_ips_donor_cases_processor(request):
    logging.info("Running Cloud Function - create_ips_donor_cases")
    blaise_service = BlaiseService()

    request_json = request.get_json()
    questionnaire_name = request_json["questionnaire_name"]
    role = request_json["role"]

    questionnaire = blaise_service.get_questionnaire("gusty", questionnaire_name)
    guid = blaise_service.get_quid("gusty", questionnaire)

    users = blaise_service.get_users("gusty")
    users_with_role = blaise_service.get_users_by_role(role)

    blaise_service.create_donor_cases(questionnaire_name, guid, users_with_role)

    return "Done!", 200
