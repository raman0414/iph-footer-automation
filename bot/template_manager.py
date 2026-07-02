class TemplateManager:

    user_templates = {}

    @classmethod
    def set_template(cls, user_id, template):

        cls.user_templates[user_id] = template

    @classmethod
    def get_template(cls, user_id):

        return cls.user_templates.get(
            user_id,
            "default"
        )