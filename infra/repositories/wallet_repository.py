import sqlite3

from core.wallet import Wallet
from infra.repositories.repository_access_generic import RepositoryAccess


class WalletSQLAccess(RepositoryAccess[Wallet]):
    def __init__(self, database_str: str) -> None:
        connection = sqlite3.connect(database_str, check_same_thread=False)
        cursor = connection.cursor()
        self.cursor = cursor

    def execute_query(self, query: None | Wallet) -> list[Wallet]:
        query_cmd: str = "select * from products"
        if query is not None:
            if query.wallet_id is not None:
                query_cmd += f"where wallet_id = {query.wallet_id}"
            elif query.owner_id is not None:
                query_cmd += f"where owner_id = {query.owner_id}"
        result = []
        cursor = self.cursor
        cursor.execute(query_cmd)
        items = cursor.fetchall()
        for item in items:
            result.append(Wallet(item[0], item[1], item[2]))
        return result

    def execute_update(self, update: Wallet) -> None:
        update_cmd: str = (
            f"update wallets set balance ={update.balance}"
            f" where wallet_id = {update.wallet_id}"
        )
        cursor = self.cursor
        cursor.execute(update_cmd)
        self.cursor.connection.commit()

    def execute_insert(self, insert: Wallet) -> None:
        arguments = f"{insert.wallet_id}, "
        arguments += f"{insert.owner_id}, {insert.balance}"
        insert_cmd: str = f"insert into products values ({arguments})"
        cursor = self.cursor
        cursor.execute(insert_cmd)
        cursor.connection.commit()
