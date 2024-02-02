from infra.repositories.database import DatabaseHandler
from infra.repositories.transaction_repository import SqlTransactionRepository
from infra.repositories.user_repository import SqlUserRepository
from infra.repositories.wallet_repository import SqlWalletRepository
from runner.cli import cli
from runner.constants import DATABASE_NAME, USERS_TABLE_NAME, USERS_TABLE_COLUMNS, WALLETS_TABLE_NAME, \
    WALLETS_TABLE_COLUMNS, TRANSACTIONS_TABLE_NAME, TRANSACTIONS_TABLE_COLUMNS


def create_database(db_name: str) -> None:
    db = DatabaseHandler(db_name)

    users_repository = SqlUserRepository(db, USERS_TABLE_NAME, USERS_TABLE_COLUMNS)
    users_repository.create()

    wallets_repository = SqlWalletRepository(db, WALLETS_TABLE_NAME, WALLETS_TABLE_COLUMNS)
    wallets_repository.create()

    transactions_repository = SqlTransactionRepository(db, TRANSACTIONS_TABLE_NAME, TRANSACTIONS_TABLE_COLUMNS)
    transactions_repository.create()


if __name__ == "__main__":
    create_database(DATABASE_NAME)
