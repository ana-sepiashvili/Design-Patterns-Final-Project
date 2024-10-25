import uuid
from uuid import UUID

from core.constants import WALLET_LIMIT
from core.errors import (
    DoesNotExistError,
    NotEnoughMoneyError,
    ThreeWalletsError,
    WrongOwnerError,
)
from core.transaction import TransactionProtocol
from core.wallet import Wallet, WalletProtocol
from infra.repositories.database import DatabaseHandler


class SqlWalletRepository:
    def __init__(self, db: DatabaseHandler, table: str, vals: str) -> None:
        self.database = db
        self.table_name = table
        self.columns = vals

    def create(self) -> None:
        self.database.create_table(self.table_name, self.columns)

    def add(self, wallet: WalletProtocol) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} "
                f"WHERE owner_id = '{wallet.get_owner_id()}'"
            )
            elems = cursor.fetchall()
            if len(elems) == WALLET_LIMIT:
                raise ThreeWalletsError
            else:
                query = f"INSERT INTO {self.table_name} VALUES (?, ?, ?)"
                cursor.execute(
                    query,
                    (
                        str(wallet.get_id()),
                        str(wallet.get_owner_id()),
                        wallet.get_bitcoin_balance(),
                    ),
                )
                connection.commit()

    def read_with_wallet_id(self, wallet_id: UUID) -> WalletProtocol:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name}" f" WHERE wallet_id = '{wallet_id}'"
            )
            values = cursor.fetchone()
            if values is None:
                raise DoesNotExistError(str(wallet_id), "Wallet")
            else:
                return Wallet(UUID(values[1]), values[2], UUID(values[0]))

    def read_with_user_id(self, user_id: UUID) -> list[WalletProtocol]:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name}" f" WHERE owner_id = '{str(user_id)}'"
            )
            values = cursor.fetchall()
            if len(values) == 0:
                return []
            else:
                result: list[WalletProtocol] = [
                    Wallet(
                        uuid.UUID(value[1]),
                        value[2],
                        uuid.UUID(value[0]),
                    )
                    for value in values
                ]
                return result

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
            if value1 is None:
                raise DoesNotExistError(str(wallet_id1), "Wallet")
            elif value2 is None:
                raise DoesNotExistError(str(wallet_id2), "Wallet")
            elif value1[0] == value2[0]:
                return True
            else:
                return False

    def make_transaction(self, transaction: TransactionProtocol) -> None:
        wallet1_id = transaction.get_to_id()
        wallet2_id = transaction.get_from_id()
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} "
                f" WHERE wallet_id = '{str(wallet1_id)}'",
            )
            value1 = cursor.fetchone()
            cursor.execute(
                f"SELECT * FROM {self.table_name} "
                f" WHERE wallet_id = '{str(wallet2_id)}'",
            )
            value2 = cursor.fetchone()
            if value1 is None:
                raise DoesNotExistError(str(wallet1_id), "Wallet")
            if value2 is None:
                raise DoesNotExistError(str(wallet2_id), "Wallet")
            if value1[2] < transaction.get_bitcoin_amount():
                raise NotEnoughMoneyError
            cursor.execute(
                f"UPDATE {self.table_name} SET bitcoin_balance = "
                f"{value1[2] + transaction.get_bitcoin_amount()}"
                f" WHERE wallet_id = '{wallet1_id}'"
            )
            new_balance = (
                value2[2]
                - transaction.get_bitcoin_amount()
                - transaction.get_bitcoin_fee()
            )
            cursor.execute(
                f"UPDATE {self.table_name} SET bitcoin_balance = "
                f"{new_balance}"
                f" WHERE wallet_id = '{wallet2_id}'"
            )
            connection.commit()

    def wallet_belongs_to_owner(self, owner_id: UUID, wallet_id: UUID) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT owner_id FROM {self.table_name}"
                + f" WHERE wallet_id = '{wallet_id}'"
            )
            values = cursor.fetchone()
            if values is None:
                raise DoesNotExistError(str(wallet_id), "Wallet")
            if str(values[0]) != str(owner_id):
                raise WrongOwnerError(str(owner_id), str(wallet_id))
