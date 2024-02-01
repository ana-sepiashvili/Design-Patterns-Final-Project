from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from infra.repositories.user_repository import UserRepository
from infra.repositories.wallet_repository import SqlWalletRepository


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.users  # type: ignore


def get_wallet_repo(request: Request) -> SqlWalletRepository:
    return request.app.state.wallets  # type: ignore


UserRepositoryDependable = Annotated[UserRepository, Depends(get_user_repository)]

WalletDep = Annotated[SqlWalletRepository, Depends(get_wallet_repo)]
