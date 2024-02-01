from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


class UserProtocol(Protocol):
    def get_email(self) -> str:
        pass

    def get_id(self) -> str:
        pass


@dataclass
class User:
    email: str
    id: UUID = field(default_factory=uuid4)

    def get_email(self) -> str:
        return self.email

    def get_id(self) -> str:
        return str(self.id)
