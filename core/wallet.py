from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Wallet:
    owner_id: UUID
    balance: float

    wallet_id: UUID = field(default_factory=uuid4)
