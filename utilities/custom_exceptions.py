class ConfigError(Exception):
    def __init__(self, message=None, missing_configs=None):
        self.message = message
        self.missing_configs = missing_configs
        super().__init__(self._format_message())

    def _format_message(self):
        if self.missing_configs:
            missing = ", ".join(self.missing_configs)
            return f"The following environment variables are not set: {missing}"

        if self.message:
            return self.message

        return "Configuration error"

    def __str__(self):
        return self._format_message()


class BlaiseError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return "Blaise error"

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


class UsersError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self._format_message())

    def _format_message(self):
        if self.message:
            return self.message
        return "Users service error"

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
