class ConfigError(Exception):
    def __init__(self, missing_configs):
        self.missing_configs = missing_configs
        super().__init__(self._format_message())

    def _format_message(self):
        missing = ", ".join(self.missing_configs)
        return (
            f"Configuration error: The following required configuration values are missing: {missing}. "
            "Please check the values are being passed correctly and try again."
        )

    def __str__(self):
        return self._format_message()


class BlaiseQuestionnaireError(Exception):
    def __init__(self, message="Blaise service error", questionnaire_name=None):
        self.message = message
        self.questionnaire_name = questionnaire_name
        super().__init__(self._format_message())

    def _format_message(self):
        base_message = self.message
        if self.questionnaire_name:
            return (
                f"Questionnaire error: {base_message}. "
                "This error occurred because the rest api failed to get the questionnaire from Blaise. "
                "Please check the VMs are online, the questionnaire is installed, and try again."
            )
        return base_message

    def __str__(self):
        return self._format_message()


class GuidError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return (
                f"{self.message}. "
                "This error occurred because the GUID service failed. "
                "Please check the questionnaire has an ID and try again"
            )
        return "GUID service error"

    def __str__(self):
        return self._format_message()


class BlaiseUsersError(Exception):
    def __init__(self, message="Blaise Users error", server_park=None):
        self.message = message
        self.server_park = server_park
        super().__init__(self._format_message())

    def _format_message(self):
        base_message = self.message
        if self.server_park:
            return f"{base_message}: Error getting users from server park {self.server_park}."
        return base_message

    def __str__(self):
        return self._format_message()


class DonorCaseError(Exception):
    pass
