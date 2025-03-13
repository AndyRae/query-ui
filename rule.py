from hutch_bunny.core.rquest_dto.rule import Rule


class CustomRule(Rule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self):
        data = super().to_dict()
        data["varcat"] = self.varcat
        return data
