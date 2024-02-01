from fastapi import FastAPI

from infra.fastapi.user import user_api
from infra.fastapi.wallet_api import wallet_api
from infra.repositories.database import DatabaseHandler
from infra.repositories.user_repository import SqlUserRepository
from infra.repositories.wallet_repository import SqlWalletRepository
from runner.constants import WALLETS_TABLE_COLUMNS, WALLETS_TABLE_NAME


def init_app(db_name: str) -> FastAPI:
    app = FastAPI()

    app.include_router(user_api)
    app.include_router(wallet_api)

    db = DatabaseHandler(db_name)

    app.state.users = SqlUserRepository(db)
    app.state.wallets = SqlWalletRepository(
        db, WALLETS_TABLE_NAME, WALLETS_TABLE_COLUMNS
    )
    return app
