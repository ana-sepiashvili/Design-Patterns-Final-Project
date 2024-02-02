import uuid
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from core.errors import ExistsError, DoesNotExistError
from core.user import User
from infra.repositories.database import DatabaseHandler


@dataclass
class SqlUserRepository:
    def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
        self.database = database
        self.table_name = table_name
        self.columns = columns

    def create(self) -> None:
        self.database.create_table(self.table_name, self.columns)

    def add(self, user: User) -> None:
        if self.__exists("email", user.get_email()):
            raise ExistsError
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table_name} VALUES(?, ?)",
                (str(user.get_id()), user.get_email()),
            )

    def exists(self, user_id: UUID) -> bool:
        return self.__exists("id", user_id)

    def __exists(self, field_name: str, value: Any) -> bool:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            result = cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE {field_name} = ?", (value,)
            ).fetchall()
            if len(result) == 0:
                return False
            return True

    def clear(self) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name}")

    def read(self, user_id: UUID) -> User:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE id = ?", (str(user_id),)
            )
            values = cursor.fetchone()
            if values is None:
                raise DoesNotExistError(str(user_id))
            else:
                return User(
                    values[1],
                    uuid.UUID(values[0]),
                )
