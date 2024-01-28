import uuid
from dataclasses import dataclass
from uuid import UUID

from core.errors import ThreeWalletsError
from infra.repositories.repository_access_generic import RepositoryAccess


@dataclass
class Wallet:
    wallet_id: UUID | None
    owner_id: UUID | None
    balance: float | None


@dataclass
class WalletRepository:
    repository: RepositoryAccess[Wallet]

    def get_all_products(self) -> list[Wallet]:
        return self.repository.execute_query(None)

    def get_wallet_with_wallet_id(self, wallet_id: UUID) -> Wallet:
        result = self.repository.execute_query(Wallet(wallet_id, None, None))
        return result[0]

    def get_wallets_with_owner_id(self, owner_id: UUID) -> list[Wallet]:
        return self.repository.execute_query(Wallet(None, owner_id, None))

    def create_new_wallet(self, owner_id: UUID) -> None:
        existing = self.get_wallets_with_owner_id(owner_id)
        if len(existing) == 3:
            raise ThreeWalletsError
        self.repository.execute_insert(Wallet(uuid.UUID(), owner_id, 100000000))

    def update_wallet(self, wallet: Wallet) -> None:
        return self.repository.execute_update(wallet)
