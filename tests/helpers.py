from appconfig.config import Config


# def mock_get_users(role):
#     return [
#         {
#             "name": "ricer",
#             "role": "DST",
#             "serverParks": [
#                 "gusty",
#             ],
#             "defaultServerPark": "gusty",
#         },
#         {
#             "name": "willij",
#             "role": role,
#             "serverParks": ["gusty", "cma"],
#             "defaultServerPark": "gusty",
#         },
#     ]

def get_default_config():
    return Config(
        blaise_api_url="blaise_api_url",
    )
