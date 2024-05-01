import pytest


class TestData:
    def __init__(self):
        self.user = "james"
        self.questionnaire_name = "IPS2306a"
        self.guid = "7bded891-3aa6-41b2-824b-0be514018806"


@pytest.fixture
def test_data():
    return TestData()
