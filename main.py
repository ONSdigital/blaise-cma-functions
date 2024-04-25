import logging
from functions.cma_functions import create_ips_donor_cases, get_users, get_quid, get_ips_field_interviewers


def create_ips_donor_cases_processer(request):
    logging.info("Running Cloud Function - create_ips_donor_cases")

    config = Config.from_env()
    config.log()
    request_json = request.get_json()

    if 'questionnaire_name' in request_json:
        questionnaire_name = request_json['questionnaire_name']
    else:
        return "No questionnaire name provided", 400
    guid = get_quid(config.server_park, questionnaire_name)

    users = get_users(config.server_park)
    ips_field_interviewers = get_ips_field_interviewers(users, "IPS Field Interviewer")

    create_ips_donor_cases(ips_field_interviewers, guid)
    return "Done!", 200
