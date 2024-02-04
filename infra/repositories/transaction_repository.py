import uuid
from uuid import UUID

from core.errors import NoAccessError, SameWalletTransactionError
from core.statistics import Statistics, StatisticsProtocol
from core.transaction import Transaction, TransactionProtocol
from infra.repositories.database import DatabaseHandler
from runner.constants import ADMIN_API_KEY


class SqlTransactionRepository:
    def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
        self.database = database
        self.table_name = table_name
        self.columns = columns
        self.create()

    def create(self) -> None:
        self.database.create_table(self.table_name, self.columns)

    def add(self, transaction: TransactionProtocol) -> None:
        if transaction.get_from_id() == transaction.get_to_id():
            raise SameWalletTransactionError()
        with self.database.connect() as connection:
            cursor = connection.cursor()
            query = f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?)"
            cursor.execute(
                query,
                (
                    str(transaction.get_id()),
                    transaction.get_from_id(),
                    transaction.get_to_id(),
                    transaction.get_bitcoin_amount(),
                    transaction.get_bitcoin_fee(),
                ),
            )
            connection.commit()

    def read_wallet_transactions(self, wallet_id: UUID) -> list[TransactionProtocol]:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE from_id = ? or to_id = ?",
                (
                    str(wallet_id),
                    str(wallet_id),
                ),
            )
            values = cursor.fetchall()
            if len(values) == 0:
                # raise NoTransactionsError(str(wallet_id))
                return []
            else:
                result: list[TransactionProtocol] = [
                    Transaction(
                        uuid.UUID(value[1]),
                        uuid.UUID(value[2]),
                        value[3],
                        value[4],
                        uuid.UUID(value[0]),
                    )
                    for value in values
                ]
                return result

    def read_statistics(self, admin_key: UUID) -> StatisticsProtocol:
        if str(admin_key) != ADMIN_API_KEY:
            raise NoAccessError(str(admin_key))

        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT COUNT(*), SUM(bitcoin_fee) FROM {self.table_name}")

            values = cursor.fetchone()
            n_transactions = values[0]
            profit = 0.0
            if n_transactions != 0:
                profit = values[1]
            return Statistics(n_transactions, profit)
