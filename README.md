# blaise-cma-functions

This repo will host cloud functions used for Case Management Application (CMA).


## Create Donor Cases
This is a HTTP triggered cloud function that uses the blaise-api-python-client to connect to the multikey endpoints of the Blaise Rest API. 
It will create a new donor case for each user with a given role (i.e. IPS Field Interviewer) in a given questionnaire (i.e. IPS2405a) if they do not already have a donor case.

example HTTP request
```python
{
    "questionnaire_name": "IPS2405a",
    "role": "IPS Field Interviewer"
}
```
example request to the `create_multikey_case` within the 'blaise_api_python_client'
```python
"cma",
        "CMA_Launcher",
        ["MainSurveyID", "ID"],
        ["25615bf2-f331-47ba-9d05-6659a513a1f2", "rich"],
        {
            "mainSurveyID": "25615bf2-f331-47ba-9d05-6659a513a1f2",
            "id": "rich",
            "cmA_ForWhom": "rich",
            "cmA_AllowSpawning": "1",
            "cmA_IsDonorCase": "1",
            "cmA_ContactData": "MainSurveyID    25615bf2-f331-47ba-9d05-6659a513a1f2    ID    rich    ContactInfoShort    IPS,May    CaseNote    This is the Donor Case. Select add case to spawn a new case with an empty shift.    Year    2024    Month    April    Stage    2303    ShiftNo    ",
        },

```

## Reissue New Donor Case

example HTTP request
```python
{
    "questionnaire_name": "IPS2405a",
    "user": "test-user"
}
```
### Local Setup

Clone the project locally:
```shell
  git clone https://github.com/ONSdigital/blaise-cma-functions.git
```

Install poetry:
```shell
  pip install poetry
```

Install dependencies:
```shell
  poetry install
```

Run make format:
```shell
  make format
```

Run make lint:
```shell
  make lint
```

Run make test:
```shell
  make test
```
