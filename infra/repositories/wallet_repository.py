from uuid import UUID

from core.errors import DoesNotExistError, ThreeWalletsError, NotEnoughMoneyError
from core.transaction import TransactionProtocol
from core.wallet import Wallet, WalletRepository
from infra.repositories.database import DatabaseHandler


class SqlWalletRepository(WalletRepository):
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
                raise DoesNotExistError(str(wallet_id))
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
            if value1 is None:
                raise DoesNotExistError(str(wallet_id1))
            elif value2 is None:
                raise DoesNotExistError(str(wallet_id2))
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
                f"SELECT * FROM {self.table_name} " f" WHERE wallet_id = ?",
                (str(wallet1_id)),
            )
            value1 = cursor.fetchone()
            cursor.execute(
                f"SELECT * FROM {self.table_name} " f" WHERE wallet_id = ?",
                (str(wallet2_id)),
            )
            value2 = cursor.fetchone()
            if value1 is None:
                raise DoesNotExistError(str(wallet1_id))
            if value2 is None:
                raise DoesNotExistError(str(wallet2_id))
            if value1[2] < transaction.get_bitcoin_amount():
                raise NotEnoughMoneyError
            cursor.execute(
                f"UPDATE {self.table_name} SET balance = "
                f"{transaction.get_bitcoin_amount() + value1[2]}"
                f" WHERE wallet_id = '{value1[0][0]}'"
            )
            cursor.execute(
                f"UPDATE {self.table_name} SET balance = "
                f"{value2[2] - transaction.get_bitcoin_amount()}"
                f" WHERE wallet_id = '{value2[0][0]}'"
            )
            connection.commit()
