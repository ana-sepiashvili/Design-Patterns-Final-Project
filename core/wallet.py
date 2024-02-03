from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from core.transaction import Transaction
from runner.constants import DEFAULT_BALANCE


@dataclass
class Wallet:
    owner_id: UUID
    balance: float = DEFAULT_BALANCE

    id: UUID = field(default_factory=uuid4)

    def get_owner_id(self) -> UUID:
        return self.owner_id

    def get_id(self) -> UUID:
        return self.id

    def get_balance(self) -> float:
        return self.balance


class WalletRepository(Protocol):
    def create(self) -> None:
        pass

    def add(self, wallet: Wallet) -> None:
        pass

    def read_with_wallet_id(self, wallet_id: UUID) -> Wallet:
        pass

    def has_same_owner(self, wallet_id1: UUID, wallet_id2: UUID) -> bool:
        pass

    def make_transaction(self, transaction: Transaction) -> None:
        pass

    def read_with_user_id(self, user_id: UUID) -> list[Wallet]:
        pass

    def wallet_belongs_to_owner(self, owner_id: UUID, wallet_id: UUID) -> None:
        pass
