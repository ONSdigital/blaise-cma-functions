class ConfigError(Exception):
    def __init__(self, message=None, missing_configs=None):
        self.message = message
        self.missing_configs = missing_configs
        super().__init__(self._format_message())

    def _format_message(self):
        if self.missing_configs:
            missing = ", ".join(self.missing_configs)
            return (
                f"The following required configuration values are missing: {missing}. "
                "Please check the values are being passed correctly and try again."
            )

        if self.message:
            return self.message

        return "Configuration error"

    def __str__(self):
        return self._format_message()


class BlaiseQuestionnaireError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return "Blaise Questionnaire error"

    def __str__(self):
        return self._format_message()


class GuidError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return "GUID service error"

    def __str__(self):
        return self._format_message()


class BlaiseUsersError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return "Blaise Users error"

    def __str__(self):
        return self._format_message()


class DonorCaseError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return "Custom Donor Case error"

    def __str__(self):
        return self._format_message()
