from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import UUID, uuid4


class UserProtocol(Protocol):
    def get_email(self) -> str:
        pass

    def get_id(self) -> UUID:
        pass


@dataclass
class User:
    email: str
    id: UUID = field(default_factory=uuid4)

    def get_email(self) -> str:
        return self.email

    def get_id(self) -> UUID:
        return self.id


class UserRepository(Protocol):
    def create(self) -> None:
        pass

    def add(self, user: User) -> None:
        pass

    def exists(self, user_id: UUID) -> bool:
        pass

    def __exists(self, field_name: str, value: Any) -> bool:
        pass

    def clear(self) -> None:
        pass

    def read(self, user_id: UUID) -> User:
        pass
