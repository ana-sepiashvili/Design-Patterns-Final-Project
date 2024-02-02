import uuid
from typing import Any
from uuid import UUID

from core.errors import DoesNotExistError
from core.transaction import Transaction, TransactionProtocol
from infra.repositories.database import DatabaseHandler


class SqlTransactionRepository:
    def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
        self.database = database
        self.table_name = table_name
        self.columns = columns
        self.create()

    def create(self) -> None:
        self.database.create_table(self.table_name, self.columns)

    def add(self, transaction: TransactionProtocol) -> None:
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

    def __result_to_list(self, values: list[list[Any]], user_id: UUID) \
            -> list[Transaction]:
        if len(values) == 0:
            raise DoesNotExistError(str(user_id))
        else:
            result = [
                Transaction(
                    uuid.UUID(value[1]),
                    uuid.UUID(value[2]),
                    value[3],
                    value[4],
                    uuid.UUID(value[0]),
                )
                for value in values
            ]
            print("PPPPPPPPPPPPPPPP")
            print(result)
            return result

    def read_user_transactions(self, user_id: UUID) -> list[Transaction]:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE user_id = ?", (str(user_id),)
            )
            values = cursor.fetchall()
            return self.__result_to_list(values, user_id)

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
            return self.__result_to_list(values, None)
