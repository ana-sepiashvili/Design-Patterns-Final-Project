from typing import Protocol
from uuid import UUID

from core.errors import DoesNotExistError, ThreeWalletsError
from core.wallet import Wallet
from infra.repositories.database import DatabaseHandler


class GenericWalletRepository(Protocol):
    def __init__(self, db: DatabaseHandler, table: str, vals: str) -> None:
        pass

    def create(self) -> None:
        pass

    def add(self, wallet: Wallet) -> None:
        pass

    def read_with_wallet_id(self, wallet_id: UUID) -> Wallet:
        pass

    def has_same_owner(self, wallet_id1: UUID, wallet_id2: UUID) -> bool:
        pass

    def make_transaction(self, transaction: list) -> None:
        pass


class SqlWalletRepository:
    def __init__(self, db: DatabaseHandler, table: str, vals: str) -> None:
        self.database = db
        self.table_name = table
        self.columns = vals
        db.create_table(self.table_name, self.columns)

    def create(self) -> None:
        self.database.create_table(self.table_name, self.columns)

    def add(self, wallet: Wallet) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} "
                f"WHERE owner_id = '{wallet.get_owner_id()}'"
            )
            elems = cursor.fetchall()
            if len(elems) == 3:
                raise ThreeWalletsError
            else:
                query = f"INSERT INTO {self.table_name} VALUES (?, ?, ?)"
                cursor.execute(
                    query,
                    (
                        str(wallet.get_id()),
                        str(wallet.get_owner_id()),
                        wallet.get_balance(),
                    ),
                )
                connection.commit()

    def read_with_wallet_id(self, wallet_id: UUID) -> Wallet:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            print("WOLIT ID")
            print(wallet_id)
            cursor.execute(
                f"SELECT * FROM {self.table_name}" f" WHERE wallet_id = '{wallet_id}'"
            )
            values = cursor.fetchone()
            if values is None:
                raise DoesNotExistError()
            else:
                return Wallet(UUID(values[1]), values[2], UUID(values[0]))

    def has_same_owner(self, wallet_id1: UUID, wallet_id2: UUID) -> bool:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT owner_id FROM {self.table_name}"
                f" WHERE wallet_id = '{wallet_id1}'"
            )
            value1 = cursor.fetchone()
            cursor.execute(
                f"SELECT owner_id FROM {self.table_name}"
                f" WHERE wallet_id = '{wallet_id2}'"
            )
            value2 = cursor.fetchone()
            if value1 is None or value2 is None:
                raise DoesNotExistError()
            elif value1[0] == value2[0]:
                return True
            else:
                return False

    def make_transaction(self, transaction: list) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} " f" WHERE wallet_id = ?", ()
            )
            values1 = cursor.fetchone()
            cursor.execute(
                f"SELECT * FROM {self.table_name} " f" WHERE wallet_id = ?", ()
            )
            values2 = cursor.fetchone()
            if values1 is None or values2 is None:
                raise DoesNotExistError()
            else:
                cursor.execute(
                    f"UPDATE {self.table_name} SET balance = {transaction}"
                    f" WHERE id = '{values1}'"
                )
                cursor.execute(
                    f"UPDATE {self.table_name} SET balance = {transaction}"
                    f" WHERE id = '{values2}'"
                )
                connection.commit()
