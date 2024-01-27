from infra.repositories.database import DatabaseHandler
from runner.constants import DATABASE_NAME


def create_database(db_name: str) -> None:
    db = DatabaseHandler(db_name)

    # unit_repository = SqlUnitRepository(db, UNITS_TABLE_NAME, UNITS_TABLE_COLUMNS)
    # unit_repository.create()


if __name__ == "__main__":
    create_database(DATABASE_NAME)
