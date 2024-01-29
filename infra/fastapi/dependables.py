from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from core.wallet import WalletRepository


def get_wallet_repo(request: Request) -> WalletRepository:
    return request.app.state.units  # type: ignore


WalletDep = Annotated[WalletRepository, Depends(get_wallet_repo)]
