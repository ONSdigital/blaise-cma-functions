import blaise_restapi

def get_quid(server_park: str, questionnaire_name: str):
    get_questionnaire_for_server_park(server_park, questionnaire_name)

def get_users():


def create_donor_case(user: str):
    print(f"Creating donor case for user {user}")
    return

def donor_case_exists(user: str):
    return True

def create_ips_donor_cases(users: list):
    for user in users:
        try:
            if not donor_case_exists(user):
                create_donor_case(user)
            else:
                print(f"Donor case already exists for user {user}")
        except Exception as e:
            print(f"Error creating donor case for user {user}")
            print(e)
    return
