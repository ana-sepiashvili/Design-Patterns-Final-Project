from fastapi import FastAPI

from infra.fastapi.user import user_api
from infra.repositories.database import DatabaseHandler
from infra.repositories.user_repository import SqlUserRepository


def init_app(db_name: str) -> FastAPI:
    app = FastAPI()

    app.include_router(user_api)

    db = DatabaseHandler(db_name)

    app.state.users = SqlUserRepository(db)

    return app
