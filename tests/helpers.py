def mock_get_users(role):
    return [
        {
            "name": "ricer",
            "role": "DST",
            "serverParks": [
                "gusty",
            ],
            "defaultServerPark": "gusty"
        },
        {
            "name": "willij",
            "role": role,
            "serverParks": [
                "gusty",
                "cma"
            ],
            "defaultServerPark": "gusty"
        }
    ]