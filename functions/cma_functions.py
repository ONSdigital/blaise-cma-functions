import logging
import blaise_restapi

restapi_client = blaise_restapi.Client(f"url")

# def get_guid(server_park: str, questionnaire_name: str) -> str:
#     try:
#         guid = blaise_restapi.get_guid(server_park, questionnaire_name) ### TODO: hit the api client endpoint here
#         logging.info(f"Got GUID {guid} for questionnaire {questionnaire_name}")
#         return guid
#     except Exception as e:
#         logging.error(f"Error getting GUID for questionnaire {questionnaire_name}: {e}")
#         return ""


def get_users(server_park: str) -> list:
    try:
        users = blaise_restapi.get_users(server_park)
        logging.info(f"Got {len(users)} users from server park {server_park}")
        return users
    except Exception as e:
        logging.error(f"Error getting users from server park {server_park}: {e}")
        return []


def get_ips_field_interviewers(users: list, role: str) -> list:
    return [user["name"] for user in users if user["role"] == role]
#
#
# def create_donor_case(field_interviewer: str, guid: str) -> None:
#     try:
#         create_donor_case(field_interviewer, guid) ### TODO: hit the api client endpoint here
#         logging.info(f"Donor case created for user {field_interviewer}")
#     except Exception as e:
#         logging.error(f"Error creating donor case for user {field_interviewer}: {e}")
#
#
# def donor_case_exists(field_interviewer: str, guid: str) -> bool:
#     try:
#         if field_interviewer in guid: ### TODO: hit the api client endpoint here
#             logging.info(f"Donor case already exists for user {field_interviewer}")
#             return True
#         else:
#             return False
#     except Exception as e:
#         logging.error(f"Error checking donor case for user {field_interviewer}: {e}")
#
#
# def create_ips_donor_cases(field_interviewers: list, guid: str) -> None:
#     for field_interviewer in field_interviewers:
#         if not donor_case_exists(field_interviewer, guid):
#             create_donor_case(field_interviewer, guid)
