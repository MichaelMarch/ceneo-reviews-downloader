from dataclasses import dataclass
import json


@dataclass
class Review:
    id: int
    author_username: str
    recommendation: str
    score: str
    date_published: str
    date_purchased: str
    content: str
    positive_votes: int
    negative_votes: int
    is_verified: bool

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)
