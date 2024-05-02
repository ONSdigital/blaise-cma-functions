from models.donor_case_model import DonorCaseModel


def test_get_questionnaire_period_info(donor_case_model_inputs):
    # Act
    donor_case_model = DonorCaseModel(
        donor_case_model_inputs.user,
        donor_case_model_inputs.questionnaire_name,
        donor_case_model_inputs.guid,
    )

    # Assert
    assert donor_case_model.full_date == "2306"
    assert donor_case_model.year == "2023"
    assert donor_case_model.month == "June"


def test_format_key_values(donor_case_model_inputs):
    # Act
    donor_case_model = DonorCaseModel(
        donor_case_model_inputs.user,
        donor_case_model_inputs.questionnaire_name,
        donor_case_model_inputs.guid,
    )
    result = donor_case_model.format_key_values()

    # Assert
    assert result == ["7bded891-3aa6-41b2-824b-0be514018806", "james"]


def test_format_key_names(donor_case_model_inputs):
    # Act
    donor_case_model = DonorCaseModel(
        donor_case_model_inputs.user,
        donor_case_model_inputs.questionnaire_name,
        donor_case_model_inputs.guid,
    )
    result = donor_case_model.format_key_names()

    # Assert
    assert result == ["MainSurveyID", "ID"]


def test_fields_for_outgoing_model(donor_case_model_inputs):
    # Act
    donor_case_model = DonorCaseModel(
        donor_case_model_inputs.user,
        donor_case_model_inputs.questionnaire_name,
        donor_case_model_inputs.guid,
    )

    # Assert
    assert donor_case_model.key_names == ["MainSurveyID", "ID"]
    assert donor_case_model.key_values == [
        "7bded891-3aa6-41b2-824b-0be514018806",
        "james",
    ]
    assert donor_case_model.data_fields == {
        "mainSurveyID": "7bded891-3aa6-41b2-824b-0be514018806",
        "id": "james",
        "cmA_ForWhom": "james",
        "cmA_AllowSpawning": "1",
        "cmA_IsDonorCase": "1",
        "cmA_ContactData": "MainSurveyID    7bded891-3aa6-41b2-824b-0be514018806    ID    james    ContactInfoShort    IPS,June    CaseNote    This is the Donor Case. Select add case to spawn a new case with an empty shift.    pii.Year    2023    pii.Month    June    pii.Stage    2306    pii.ShiftNo    '",
    }