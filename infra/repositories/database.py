import sqlite3
from sqlite3 import Connection
from typing import Protocol


class Database(Protocol):
    def __init__(self, db_name: str) -> None:
        pass

    def connect(self) -> Connection:
        pass

    def create_table(self, table_name: str, columns: str) -> None:
        pass


class DatabaseHandler:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def connect(self) -> Connection:
        return sqlite3.connect(self.db_name)

    def create_table(self, table_name: str, columns: str) -> None:
        with self.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
