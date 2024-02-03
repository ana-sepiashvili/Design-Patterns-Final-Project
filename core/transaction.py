import uuid
from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from core.statistics import Statistics


@dataclass
class Transaction:
    from_id: UUID
    to_id: UUID
    bitcoin_amount: float
    bitcoin_fee: float = 0.0

    id: UUID = field(default_factory=uuid4)

    def get_id(self) -> UUID:
        return self.id

    def get_from_id(self) -> UUID:
        return self.from_id

    def get_to_id(self) -> UUID:
        return self.to_id

    def get_bitcoin_amount(self) -> float:
        return self.bitcoin_amount

    def get_bitcoin_fee(self) -> float:
        return self.bitcoin_fee


class TransactionRepository(Protocol):
    def create(self) -> None:
        pass

    def add(self, transaction: Transaction) -> None:
        pass

    def read_wallet_transactions(self, wallet_id: uuid.UUID) -> list[Transaction]:
        pass

    def read_statistics(self, admin_key: UUID) -> Statistics:
        pass
