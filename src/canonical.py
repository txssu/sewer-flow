from dataclasses import dataclass, asdict
import json


@dataclass
class CanonicalUpdate:
    user_id: str
    text: str
    sent_at: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))
