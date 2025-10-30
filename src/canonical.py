from dataclasses import dataclass, asdict
import json


@dataclass
class CanonicalUpdate:
    user_id: str
    text: str

    def to_json(self) -> str:
        return json.dumps(asdict(self))
