import pytest


class DonorCaseModelInputs:
    def __init__(self):
        self.user = "james"
        self.questionnaire_name = "IPS2306a"
        self.guid = "7bded891-3aa6-41b2-824b-0be514018806"


@pytest.fixture
def donor_case_model_inputs():
    return DonorCaseModelInputs()


@pytest.fixture
def mock_get_list_of_users():
    return [
        {
            "name": "rich",
            "role": "DST",
            "serverParks": ["gusty", "cma"],
            "defaultServerPark": "gusty",
        },
        {
            "name": "sarah",
            "role": "DST",
            "serverParks": ["gusty"],
            "defaultServerPark": "gusty",
        },
    ]


@pytest.fixture
def mock_get_questionnaire():
    return {
        "name": "LMS2309_GO1",
        "id": "25615bf2-f331-47ba-9d05-6659a513a1f2",
        "serverParkName": "gusty",
        "installDate": "2024-04-24T09:49:34.2685322+01:00",
        "status": "Active",
        "dataRecordCount": 0,
        "hasData": False,
        "blaiseVersion": "5.9.9.2735",
        "nodes": [
            {"nodeName": "blaise-gusty-mgmt", "nodeStatus": "Active"},
            {"nodeName": "blaise-gusty-data-entry-1", "nodeStatus": "Active"},
            {"nodeName": "blaise-gusty-data-entry-2", "nodeStatus": "Active"},
        ],
    }
