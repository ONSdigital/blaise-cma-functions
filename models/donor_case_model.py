import re
from datetime import datetime


class DonorCaseModel:
    def __init__(self, user, questionnaire_name, guid):
        self.user = user
        self.questionnaire_name = questionnaire_name
        self.guid = guid

        self.full_date = self.get_full_date()
        self.year = self.get_year()
        self.month = self.get_month()

        self.key_names = self.format_key_names()
        self.key_values = self.format_key_values()
        self.data_fields = self.format_data_fields()

    def format_data_fields(self):
        return {
            "mainSurveyID": f"{self.guid}",
            "id": f"{self.user}",
            "cmA_ForWhom": f"{self.user}",
            "cmA_AllowSpawning": "1",
            "cmA_IsDonorCase": "1",
            "cmA_ContactData": f"MainSurveyID    {self.guid}    ID    {self.user}    ContactInfoShort    IPS,{self.month}    CaseNote    This is the Donor Case. Select add case to spawn a new case with an empty shift.    Year    {self.year}    Month    {self.month}    Stage    {self.full_date}    ShiftNo    '",
        }

    def format_key_values(self) -> list[str]:
        return [self.guid, self.user]

    def format_key_names(self) -> list[str]:
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
            return datetime.strptime(match.group(3), "%m").strftime("%B")
