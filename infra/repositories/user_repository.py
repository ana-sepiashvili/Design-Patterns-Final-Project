import uuid
from dataclasses import dataclass
from uuid import UUID

from core.errors import DoesNotExistError, ExistsError
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
        with self.database.connect() as connection:
            cursor = connection.cursor()
            result = cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE email = ?", (user.get_email(),)
            ).fetchall()
            if len(result) != 0:
                raise ExistsError
            cursor.execute(
                f"INSERT INTO {self.table_name} VALUES(?, ?)",
                (str(user.get_id()), user.get_email()),
            )

    def read(self, user_id: UUID) -> User:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE id = ?", (str(user_id),)
            )
            result = cursor.fetchone()
            if result is None:
                raise DoesNotExistError(str(user_id))
            else:
                return User(
                    result[1],
                    uuid.UUID(result[0]),
                )

    def clear(self) -> None:
        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name}")
