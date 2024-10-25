from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from core.constants import DEFAULT_BALANCE
from core.transaction import TransactionProtocol


class WalletProtocol(Protocol):
    def get_owner_id(self) -> UUID:
        pass

    def get_id(self) -> UUID:
        pass

    def get_bitcoin_balance(self) -> float:
        pass


@dataclass
class Wallet:
    owner_id: UUID
    bitcoin_balance: float = DEFAULT_BALANCE

    id: UUID = field(default_factory=uuid4)

    def get_owner_id(self) -> UUID:
        return self.owner_id

    def get_id(self) -> UUID:
        return self.id

    def get_bitcoin_balance(self) -> float:
        return self.bitcoin_balance


class WalletRepository(Protocol):
    def create(self) -> None:
        pass

    def add(self, wallet: WalletProtocol) -> None:
        pass

    def read_with_wallet_id(self, wallet_id: UUID) -> WalletProtocol:
        pass

    def has_same_owner(self, wallet_id1: UUID, wallet_id2: UUID) -> bool:
        pass

    def make_transaction(self, transaction: TransactionProtocol) -> None:
        pass

    def read_with_user_id(self, user_id: UUID) -> list[WalletProtocol]:
        pass

    def wallet_belongs_to_owner(self, owner_id: UUID, wallet_id: UUID) -> None:
        pass
