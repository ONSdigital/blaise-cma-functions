from functions.cma_functions import create_ips_donor_cases, get_quid, get_users
def create_cma_donor_cases(request):
    #TODO: Take the questionnaire name
    #TODO: Look up the GUID using the questionnaire name
    #TODO: Get all IPS user ids out of baise db
    #TODO: Iterate though each user and create a donor case for each user - IF the donor case doesn't already exist
    print(f"Running Cloud Function - create_cma_donor_cases")
    config = Config.from_env()
    config.log()

    request_json = request.get_json()
    if 'questionnaire_name' in request_json:
        questionnaire_name = request_json['instrument_name']

    guid = get_quid(config.server_park, questionnaire_name)
    users = get_users(config.server_park)
    ips_users = [user for user in users if user['user_type'] == 'IPS']
    create_ips_donor_cases(ips_users)

    return "Done!"
