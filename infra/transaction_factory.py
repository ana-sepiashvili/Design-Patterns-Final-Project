from dataclasses import dataclass
from uuid import UUID

from core.transaction import Transaction
from core.wallet import WalletRepository
from runner.constants import TRANSACTION_FEE


@dataclass
class TransactionFactory:
    wallets: WalletRepository

    def create_transaction(self, from_id: UUID, to_id: UUID, bitcoin_amount: float) -> Transaction:
        if self.wallets.has_same_owner(from_id, to_id):
            return Transaction(**{
                "from_id": from_id,
                "to_id": to_id,
                "bitcoin_amount": bitcoin_amount,
            })
        else:
            transaction_fee = bitcoin_amount * TRANSACTION_FEE
            return Transaction(
                from_id=from_id,
                to_id=to_id,
                bitcoin_amount=bitcoin_amount - transaction_fee,
                bitcoin_fee=transaction_fee,
            )
