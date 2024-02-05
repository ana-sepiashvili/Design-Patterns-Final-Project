import uuid

from core.user import User
from core.wallet import Wallet
from infra.repositories.database import DatabaseHandler
from infra.repositories.transaction_repository import SqlTransactionRepository
from infra.repositories.user_repository import SqlUserRepository
from infra.repositories.wallet_repository import SqlWalletRepository
from core.constants import (
    DATABASE_NAME,
    TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS,
    TEST_USER1_EMAIL,
    TEST_USER1_ID,
    TEST_USER1_WALLET1,
    TEST_USER1_WALLET2,
    TEST_USER2_EMAIL,
    TEST_USER2_ID,
    TEST_USER2_WALLET,
    TRANSACTIONS_TABLE_COLUMNS,
    TRANSACTIONS_TABLE_NAME,
    USERS_TABLE_COLUMNS,
    USERS_TABLE_NAME,
    WALLETS_TABLE_COLUMNS,
    WALLETS_TABLE_NAME,
)


def create_database(db_name: str) -> None:
    db = DatabaseHandler(db_name)

    users_repository = SqlUserRepository(db, USERS_TABLE_NAME, USERS_TABLE_COLUMNS)
    users_repository.create()

    wallets_repository = SqlWalletRepository(
        db, WALLETS_TABLE_NAME, WALLETS_TABLE_COLUMNS
    )
    wallets_repository.create()
    insert_default_values(db_name, users_repository, wallets_repository)

    transactions_repository = SqlTransactionRepository(
        db, TRANSACTIONS_TABLE_NAME, TRANSACTIONS_TABLE_COLUMNS
    )
    transactions_repository.create()


def insert_default_values(
    db_name: str,
    user_repository: SqlUserRepository,
    wallet_repository: SqlWalletRepository,
) -> None:
    if db_name == TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS:
        user1 = User(TEST_USER1_EMAIL, uuid.UUID(TEST_USER1_ID))
        user2 = User(TEST_USER2_EMAIL, uuid.UUID(TEST_USER2_ID))
        user_repository.add(user1)
        user_repository.add(user2)

        wallet_repository.add(
            Wallet(user1.get_id(), 1.0, uuid.UUID(TEST_USER1_WALLET1))
        )
        wallet_repository.add(
            Wallet(user1.get_id(), 1.0, uuid.UUID(TEST_USER1_WALLET2))
        )
        wallet_repository.add(Wallet(user2.get_id(), 1.0, uuid.UUID(TEST_USER2_WALLET)))


if __name__ == "__main__":
    create_database(DATABASE_NAME)
