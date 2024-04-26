import pytest


@pytest.fixture()
def mock_get_guestionnaires():
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
            {
                "nodeName": "blaise-gusty-mgmt",
                "nodeStatus": "Active"
            },
            {
                "nodeName": "blaise-gusty-data-entry-1",
                "nodeStatus": "Active"
            },
            {
                "nodeName": "blaise-gusty-data-entry-2",
                "nodeStatus": "Active"
            }
        ]
    }


@pytest.fixture()
def mock_donor_case_info():
    return {
        "MainSurveyID" : '7bded891-3aa6-41b2-824b-0be514018806',
        "CMA_IsDonorCase" : 'yes',
        "CMA_AllowSpawning" : 'yes',
        "CMA_ForWhom" : 'rich',
        "ID" : 'rich',
        "CMA_ContactData" : 'MainSurveyID <TAB> 7bded891-3aa6-41b2-824b-0be514018806 <TAB> ID <TAB> rich <TAB> ContactInfoShort <TAB> IPS,June <TAB> CaseNote <TAB> This is the Donor Case. Select add case to spawn a new case with an empty shift. <TAB> pii.Year <TAB> 2023 <TAB> pii.Month <TAB> June <TAB> pii.Stage <TAB> 2306 <TAB> pii.ShiftNo <TAB> '
    }


@pytest.fixture()
def mock_questionnaire_report():
    return {
  "questionnaireName": "cma_launcher",
  "questionnaireId": "b0425080-2470-49db-bb53-170633c4fbba",
  "reportingData": [
    {
        "cmA_ForWhom": "rich"
    },
    {
        "cmA_ForWhom": "james"
    },
    {
        "cmA_ForWhom": "rich"
    }
    ]
}