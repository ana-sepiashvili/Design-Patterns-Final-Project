from dataclasses import dataclass
from typing import Any
from uuid import UUID

from core.errors import ExistsError
from core.user import User
from infra.repositories.database import DatabaseHandler
from runner.constants import USERS_TABLE_COLUMNS, USERS_TABLE_NAME


class UserRepository(Protocol):
    def create(self) -> None:
        pass

    def add(self, user: User) -> None:
        pass

    def exists(self, user_id: UUID) -> bool:
        pass

    def __exists(self, field_name: str, value: Any) -> bool:
        pass

    def clear(self) -> None:
        pass


@dataclass
class SqlUserRepository:
    database: DatabaseHandler

    def __post_init__(self) -> None:
        self.table: str = USERS_TABLE_NAME
        self.columns: str = USERS_TABLE_COLUMNS
        self.create()

    def create(self) -> None:
        self.database.create_table(self.table, self.columns)

    def add(self, user: User) -> None:
        if self.__exists("email", user.get_email()):
            raise ExistsError
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table} VALUES(?, ?)",
                (str(user.get_id()), user.get_email()),
            )

    def exists(self, user_id: UUID) -> bool:
        return self.__exists("id", user_id)

    def __exists(self, field_name: str, value: Any) -> bool:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            result = cursor.execute(
                f"SELECT * FROM {self.table} WHERE {field_name} = ?", (value,)
            ).fetchall()
            if len(result) == 0:
                return False
            return True

    def clear(self) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {self.table}")
