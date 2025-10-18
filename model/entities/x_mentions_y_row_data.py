from dataclasses import dataclass, astuple


@dataclass
class XMentionsYRowData:
    speaker: str
    character_addressed: str
    book: int
    episode: int
    full_line: str

    def __iter__(self):
        return iter(astuple(self))

    def __getitem__(self, name):
        return getattr(self, name)
