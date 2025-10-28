from dataclasses import dataclass, asdict
import json


@dataclass
class UserId:
    type: str
    value: str


@dataclass
class UserFrom:
    fullname: str
    username: str | None
    language_code: str | None


@dataclass
class Attachment:
    type: str
    encoding: str
    data: str


@dataclass
class CanonicalUpdate:
    id: UserId
    from_user: UserFrom
    text: str | None
    sent_at: str
    attachment: Attachment | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)
