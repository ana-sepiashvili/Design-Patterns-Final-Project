from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Wallet:
    owner_id: UUID
    balance: float

    id: UUID = field(default_factory=uuid4)

    def get_owner_id(self) -> UUID:
        return self.owner_id

    def get_id(self) -> UUID:
        return self.id

    def get_balance(self) -> float:
        return self.balance
