from fastapi import FastAPI

from infra.repositories.database import DatabaseHandler


def init_app(db_name: str) -> FastAPI:
    app = FastAPI()

    # app.include_router(unit_api)

    db = DatabaseHandler(db_name)

    # app.state.units = SqlUnitRepository(db, UNITS_TABLE_NAME, UNITS_TABLE_COLUMNS)

    return app
