from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from core.wallet import WalletRepository
from infra.repositories.user_repository import SqlUserRepository


def get_user_repository(request: Request) -> SqlUserRepository:
    return request.app.state.users  # type: ignore


def get_wallet_repo(request: Request) -> WalletRepository:
    return request.app.state.units  # type: ignore


UserRepositoryDependable = Annotated[SqlUserRepository, Depends(get_user_repository)]

WalletDep = Annotated[WalletRepository, Depends(get_wallet_repo)]
