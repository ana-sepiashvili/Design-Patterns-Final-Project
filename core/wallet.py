from dataclasses import dataclass, field
from uuid import UUID, uuid4

from core.errors import DoesNotExistError, ThreeWalletsError
from infra.repositories.repository_access_generic import RepositoryAccess


@dataclass
class Wallet:
    owner_id: UUID | None
    balance: float | None

    wallet_id: UUID | None = field(default_factory=uuid4)


@dataclass
class WalletRepository:
    repository: RepositoryAccess[Wallet]

    def get_wallet_with_wallet_id(self, wallet_id: UUID) -> Wallet:
        result = self.repository.execute_query(Wallet(None, None, wallet_id))
        if len(result) == 0:
            raise DoesNotExistError
        return result[0]

    def get_wallets_with_owner_id(self, owner_id: UUID | None) -> list[Wallet]:
        return self.repository.execute_query(Wallet(owner_id, None, None))

    def create_new_wallet(self, wallet: Wallet) -> None:
        wallet_id = wallet.wallet_id
        owner_id = wallet.owner_id
        existing = self.get_wallets_with_owner_id(wallet.owner_id)
        if len(existing) == 3:
            raise ThreeWalletsError
        self.repository.execute_insert(Wallet(owner_id, 100000000, wallet_id))
