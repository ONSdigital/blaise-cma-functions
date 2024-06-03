class ConfigError(Exception):
    def __init__(self, message="Configuration error", missing_configs=None):
        self.message = message
        self.missing_configs = missing_configs
        super().__init__(self._format_message())

    def _format_message(self):
        base_message = self.message
        if self.missing_configs:
            missing = ", ".join(self.missing_configs)
            return f"{base_message}: Missing configurations - {missing}"
        return base_message

    def __str__(self):
        return self._format_message()


class QuestionnaireError(Exception):
    def __init__(self, message="Questionnaire error", questionnaire_name=None):
        self.message = message
        self.questionnaire_name = questionnaire_name
        super().__init__(self._format_message())

    def _format_message(self):
        base_message = self.message
        if self.questionnaire_name:
            return f"{base_message}: Could not find questionnaire - {self.questionnaire_name}"
        return base_message

    def __str__(self):
        return self._format_message()
