from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from core.statistics import StatisticsRepository
from core.transaction import TransactionRepository
from core.user import UserRepository
from core.wallet import WalletRepository


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.users  # type: ignore


def get_wallet_repository(request: Request) -> WalletRepository:
    return request.app.state.wallets  # type: ignore


def get_transaction_repository(request: Request) -> TransactionRepository:
    return request.app.state.transactions  # type: ignore


def get_statistics_repository(request: Request) -> StatisticsRepository:
    return request.app.state.statistics  # type: ignore


UserRepositoryDependable = Annotated[UserRepository, Depends(get_user_repository)]

WalletRepositoryDependable = Annotated[WalletRepository, Depends(get_wallet_repository)]

TransactionRepositoryDependable = Annotated[
    TransactionRepository, Depends(get_transaction_repository)
]

StatisticsRepositoryDependable = Annotated[
    StatisticsRepository, Depends(get_statistics_repository)
]
