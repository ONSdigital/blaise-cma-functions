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
    assert donor_case_model.tla == "IPS"
    assert donor_case_model.last_day_of_month == "30-06-2023"


def test_get_questionnaire_period_info_on_ips_pilot_questionnaire(
    donor_case_model_inputs,
):
    # Act
    donor_case_model = DonorCaseModel(
        donor_case_model_inputs.user,
        "IPS2500A",
        donor_case_model_inputs.guid,
    )

    # Assert
    assert donor_case_model.full_date == "2500"
    assert donor_case_model.year == "2025"
    assert donor_case_model.month == "January"
    assert donor_case_model.tla == "IPS"
    assert donor_case_model.last_day_of_month == "31-01-2025"


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
        "cmA_EndDate": "30-06-2023",
        "cmA_ContactData": "MainSurveyID\t7bded891-3aa6-41b2-824b-0be514018806\tID\tjames\tCaseNote\tThis is the Donor Case. Select the add case button to spawn a new case with an empty shift. Then select the show all cases filter to show the case.\tcaseinfo.Year\t2023\tcaseinfo.Survey\tIPS\tcaseinfo.Month\tJune\tcaseinfo.ShiftNo\t\tcaseinfo.IOut\t",
    }


def test_double_tab_after_shift_no_in_outgoing_model(donor_case_model_inputs):
    # Arrange
    expected_pattern = "caseinfo.ShiftNo\t\t"

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
    assert expected_pattern in donor_case_model.data_fields["cmA_ContactData"]
