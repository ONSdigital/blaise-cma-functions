import calendar
import logging
import re
from datetime import datetime
from typing import Any

from utilities.custom_exceptions import InvalidQuestionnaireMonth
from utilities.logging import function_name


class DonorCaseModel:
    def __init__(
        self, user: str, questionnaire_name: str, guid: str, donor_case_prefix: str = ""
    ) -> None:
        self.user = user
        self.questionnaire_name = questionnaire_name
        self.guid = guid
        self.donor_case_prefix = donor_case_prefix

        self.full_date = self.get_full_date()
        self.year = self.get_year()
        self.month = self.get_month()
        self.last_day_of_month = self.calculate_last_day_of_month()
        self.tla = self.get_tla()

        self.key_names = self.format_key_names()
        self.key_values = self.format_key_values()
        self.data_fields = self.format_data_fields()

    def format_data_fields(self) -> dict[str, Any]:
        return {
            "mainSurveyID": f"{self.guid}",
            "id": f"{self.donor_case_prefix}{self.user}",
            "cmA_ForWhom": f"{self.user}",
            "cmA_AllowSpawning": "1",
            "cmA_IsDonorCase": "1",
            "cmA_EndDate": f"{self.last_day_of_month}",
            "cmA_ContactData": f"MainSurveyID\t{self.guid}\tID\t{self.donor_case_prefix}{self.user}\tCaseNote\tThis is the Donor Case. Select the add case button to spawn a new case with an empty shift. \tcaseinfo.Year\t{self.year}\tcaseinfo.Survey\t{self.tla}\tcaseinfo.Month\t{self.month}\tcaseinfo.ShiftNo\t\tcaseinfo.IOut\t",
        }

    def format_key_values(self) -> list[str]:
        return [self.guid, self.user]

    @staticmethod
    def format_key_names() -> list[str]:
        return ["MainSurveyID", "ID"]

    def get_full_date(self):
        pattern = r"([A-Za-z]+)(\d{2})(\d{2})"
        match = re.match(pattern, self.questionnaire_name)
        if match:
            return match.group(2) + match.group(3)

    def get_year(self):
        pattern = r"([A-Za-z]+)(\d{2})(\d{2})"
        match = re.match(pattern, self.questionnaire_name)
        if match:
            return "20" + match.group(2)

    def get_month(self):
        pattern = r"([A-Za-z]+)(\d{2})(\d{2})"
        match = re.match(pattern, self.questionnaire_name)
        if match:
            month_str = match.group(3)
            try:
                return datetime.strptime(month_str, "%m").strftime("%B")
            except ValueError as e:
                error_message = (
                    f"Exception caught in {function_name()}. "
                    f"Error getting month from questionnaire name: {self.questionnaire_name}: {e}"
                )
                logging.error(error_message)
                raise InvalidQuestionnaireMonth(error_message)

    def get_tla(self):
        pattern = r"^[a-zA-Z]{3}"
        match = re.match(pattern, self.questionnaire_name)
        return match.group(0)[:3] if match else None

    def calculate_last_day_of_month(self):
        month_number = list(calendar.month_name).index(self.month)
        num_days = calendar.monthrange(int(self.year), month_number)[1]
        return datetime(int(self.year), month_number, num_days).strftime("%d-%m-%Y")

    def is_pilot(self):
        return self.questionnaire_name.lower().endswith("_pilot")
