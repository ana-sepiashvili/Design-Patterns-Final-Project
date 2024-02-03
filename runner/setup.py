from fastapi import FastAPI

from infra.fastapi.statistics_api import statistics_api
from infra.fastapi.transaction_api import transaction_api
from infra.fastapi.user_api import user_api
from infra.fastapi.wallet_api import wallet_api
from infra.repositories.database import DatabaseHandler
from infra.repositories.transaction_repository import SqlTransactionRepository
from infra.repositories.user_repository import SqlUserRepository
from infra.repositories.wallet_repository import SqlWalletRepository
from runner.constants import (
    TRANSACTIONS_TABLE_COLUMNS,
    TRANSACTIONS_TABLE_NAME,
    USERS_TABLE_COLUMNS,
    USERS_TABLE_NAME,
    WALLETS_TABLE_COLUMNS,
    WALLETS_TABLE_NAME,
)


def init_app(db_name: str) -> FastAPI:
    app = FastAPI()

    app.include_router(user_api)
    app.include_router(wallet_api)
    app.include_router(transaction_api)
    app.include_router(statistics_api)

    db = DatabaseHandler(db_name)

    app.state.users = SqlUserRepository(db, USERS_TABLE_NAME, USERS_TABLE_COLUMNS)
    app.state.wallets = SqlWalletRepository(
        db, WALLETS_TABLE_NAME, WALLETS_TABLE_COLUMNS
    )
    app.state.transactions = SqlTransactionRepository(
        db, TRANSACTIONS_TABLE_NAME, TRANSACTIONS_TABLE_COLUMNS
    )
    return app
