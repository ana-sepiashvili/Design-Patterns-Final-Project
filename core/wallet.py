from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Wallet:
    owner_id: UUID | None
    balance: float | None

    wallet_id: UUID | None = field(default_factory=uuid4)
