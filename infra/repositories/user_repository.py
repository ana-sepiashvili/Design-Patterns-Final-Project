from dataclasses import dataclass
from typing import Any
from uuid import UUID

from core.errors import ExistsError
from core.user import User
from infra.repositories.database import DatabaseHandler


@dataclass
class UserRepository:
    database: DatabaseHandler

    def __post_init__(self) -> None:
        self.table: str = "users"
        self.fields: str = "(id UUID UNIQUE, " "email TEXT NOT NULL UNIQUE)"
        self.create()

    def create(self) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table} ({self.fields})")
            connection.commit()

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
