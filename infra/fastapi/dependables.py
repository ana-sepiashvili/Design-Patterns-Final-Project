from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from core.transaction import TransactionRepository
from infra.repositories.user_repository import UserRepository


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.users  # type: ignore


def get_wallet_repo(request: Request) -> WalletRepository:
    return request.app.state.units  # type: ignore


def get_transaction_repository(request: Request) -> TransactionRepository:
    return request.app.state.transactions  # type: ignore


UserRepositoryDependable = Annotated[UserRepository, Depends(get_user_repository)]

WalletDep = Annotated[WalletRepository, Depends(get_wallet_repo)]

TransactionRepositoryDependable = Annotated[
    TransactionRepository, Depends(get_user_repository)
]
