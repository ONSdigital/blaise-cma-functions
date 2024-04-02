import pytest


@pytest.fixture
def mock_get_users():
    return [
        {
            "name": "Rich",
            "role": "DST",
            "serverParks": [
                "gusty",
                "cma"
            ],
            "defaultServerPark": "gusty"
        },
        {
            "name": "James",
            "role": "IPS Field Interviewer",
            "serverParks": [
                "gusty",
                "cma"
            ],
            "defaultServerPark": "gusty"
        }
    ]

@pytest.fixture
def mock_get_users_without_ips():
    return [
        {
            "name": "Rich",
            "role": "DST",
            "serverParks": [
                "gusty",
                "cma"
            ],
            "defaultServerPark": "gusty"
        },
        {
            "name": "James",
            "role": "DST",
            "serverParks": [
                "gusty",
                "cma"
            ],
            "defaultServerPark": "gusty"
        }
    ]


@pytest.fixture
def mock_get_user_roles():
    return [
  {
    "name": "BDSS",
    "description": "Role for BDSS users",
  },
{
    "name": "DST",
    "description": "Role for DST users",
  },
  {
    "name": "IPS Field Interviewer",
    "description": "Role for IPS Field Interviewers",
  },
]