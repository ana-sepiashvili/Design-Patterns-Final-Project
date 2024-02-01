from fastapi import FastAPI

from infra.fastapi.wallet_api import wallet_api
from infra.repositories.database import DatabaseHandler
from infra.repositories.wallet_repository import SqlWalletRepository
from runner.constants import WALLETS_TABLE_COLUMS, WALLETS_TABLE_NAME


def init_app(db_name: str) -> FastAPI:
    app = FastAPI()

    # app.include_router(unit_api)
    app.include_router(wallet_api)
    db = DatabaseHandler(db_name)
    app.state.wallets = SqlWalletRepository(
        db, WALLETS_TABLE_NAME, WALLETS_TABLE_COLUMS
    )
    # app.state.units = SqlUnitRepository(db, UNITS_TABLE_NAME, UNITS_TABLE_COLUMNS)

    return app
