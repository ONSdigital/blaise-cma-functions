# Blaise CMA Functions

This repository contains Google Cloud Functions used for the Blaise Case Management Application (CMA). CMA is a specialised application deployed to Blaise for managing CAPI mode data collection.

## Cloud Functions

### Create Donor Cases

An HTTP-triggered Cloud Function that creates donor cases for users with specific roles in a given questionnaire. This function uses the `blaise-api-python-client` to interact with Blaise via our REST API wrapper.

Request Format:

```json
{
    "questionnaire_name": "IPS2405a",
    "role": "IPS Field Interviewer"
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| questionnaire_name | string | The name of the questionnaire (e.g., "IPS2405a") |
| role | string | The role to create donor cases for (e.g., "IPS Field Interviewer") |

### Reissue Donor Case

An HTTP-triggered Cloud Function that reissues a donor case for a specific user in a given questionnaire. This function uses the `blaise-api-python-client` to interact with Blaise via our REST API wrapper.

Request Format:

```json
{
    "questionnaire_name": "IPS2405a",
    "user": "test-user"
}
```

| Parameter | Type | Description |
|-----------|------|-------------|
| questionnaire_name | string | The name of the questionnaire |
| user | string | The username to reissue the donor case for |

## Implementation Details

The functions use the `blaise-api-python-client` to create entries in the `CMA_Launcher` database with the following structure:

```python
{
    "mainSurveyID": "<uuid>",
    "id": "<username>",
    "cmA_ForWhom": "<username>",
    "cmA_AllowSpawning": "1",
    "cmA_IsDonorCase": "1",
    "cmA_ContactData": "MainSurveyID    <uuid>    ID    <username>    ContactInfoShort    <survey_info>    CaseNote    This is the Donor Case. Select add case to spawn a new case with an empty shift.    Year    <year>    Month    <month>    Stage    <stage>    ShiftNo    "
}
```

## Local Development Setup

1. Clone the project locally:

   ```shell
   git clone https://github.com/ONSdigital/blaise-cma-functions.git
   cd blaise-cma-functions
   ```

2. Install Poetry if you haven't already:

   ```shell
   pip install poetry
   ```

3. Install project dependencies:

   ```shell
   poetry install
   ```

The following environment variables are required:

| Variable | Description |
|----------|-------------|
| BLAISE_API_URL | The URL of the Blaise REST API |
| BLAISE_SERVER_PARK | The Blaise server park name |

## Development Commands

This project uses `make` commands to streamline development tasks. The following commands are available:

Format code using black and isort:

```shell
make format
```

Lint code using flake8 and mypy:

```shell
make lint
```

Run the test suite using pytest:

```shell
make test
```
