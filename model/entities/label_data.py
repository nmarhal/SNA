class LabelData:
    def __init__(self, label_name: str, character_name_to_metric: dict[str, float]):
        self.label_name = label_name
        self.character_name_to_metric = character_name_to_metric