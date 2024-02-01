from uuid import UUID

from core.errors import DoesNotExistError, ThreeWalletsError
from core.wallet import Wallet
from infra.repositories.database import DatabaseHandler


class SqlWalletRepository:
    def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
        self.database = database
        self.table_name = table_name
        self.columns = columns

    def create(self) -> None:
        self.database.create_table(self.table_name, self.columns)

    def add(self, wallet: Wallet) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} "
                f"WHERE owner_id = {wallet.owner_id}"
            )
            elems = cursor.fetchall()
            if len(elems) == 3:
                raise ThreeWalletsError
            else:
                query = f"INSERT INTO {self.table_name} VALUES (?, ?, ?)"
                cursor.execute(
                    query,
                    (wallet.wallet_id, wallet.owner_id, wallet.balance),
                )
                connection.commit()

    def read_with_wallet_id(self, wallet_id: UUID) -> Wallet:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name}"
                f" WHERE wallet_id = {wallet_id}"
            )
            values = cursor.fetchone()
            if values is None:
                raise DoesNotExistError()
            else:
                return Wallet(UUID(values[1]), values[2], UUID(values[0]))

    def make_transaction(self, transaction: list) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", ())
            values1 = cursor.fetchone()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", ())
            values2 = cursor.fetchone()
            if values1 is None or values2 is None:
                raise DoesNotExistError()
            else:
                cursor.execute(
                    f"UPDATE {self.table_name} SET balance = {transaction}"
                    f"WHERE id = '{values1}'"
                )
                cursor.execute(
                    f"UPDATE {self.table_name} SET balance = {transaction}"
                    f" WHERE id = '{values2}'"
                )
                connection.commit()
