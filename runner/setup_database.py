from infra.repositories.database import DatabaseHandler
from infra.repositories.user_repository import SqlUserRepository
from runner.constants import DATABASE_NAME, USERS_TABLE_NAME, USERS_TABLE_COLUMNS


def create_database(db_name: str) -> None:
    db = DatabaseHandler(db_name)

    user_repository = SqlUserRepository(db, USERS_TABLE_NAME, USERS_TABLE_COLUMNS)
    user_repository.create()


if __name__ == "__main__":
    create_database(DATABASE_NAME)
