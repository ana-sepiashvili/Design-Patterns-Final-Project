from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from core.transaction import TransactionProtocol
from infra.repositories.database import DatabaseHandler


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


class WalletRepository(Protocol):
    def __init__(self, db: DatabaseHandler, table: str, vals: str) -> None:
        pass

    def create(self) -> None:
        pass

    def add(self, wallet: Wallet) -> None:
        pass

    def read_with_wallet_id(self, wallet_id: UUID) -> Wallet:
        pass

    def has_same_owner(self, wallet_id1: UUID, wallet_id2: UUID) -> bool:
        pass

    def make_transaction(self, transaction: TransactionProtocol) -> None:
        pass
