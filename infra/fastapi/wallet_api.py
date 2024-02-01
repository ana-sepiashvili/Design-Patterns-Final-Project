from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import DoesNotExistError, ThreeWalletsError
from core.wallet import Wallet
from infra.fastapi.dependables import WalletDep

wallet_api = APIRouter(tags=["Wallets"])


class CreateWalletReqt(BaseModel):
    owner_id: UUID
    balance: float


class WalletResp(BaseModel):
    wallet_id: UUID
    balance_btc: float
    balance_usd: float


class TransacListResp(BaseModel):
    transactions: list


@wallet_api.post("/wallet", status_code=201, response_model=WalletResp)
def create_wallet(
    request: CreateWalletReqt, wallets: WalletDep
) -> dict[str, Any] | JSONResponse:
    wallet = Wallet(**request.dict())

    try:
        wallets.add(wallet)
    except ThreeWalletsError:
        err_msg = f"User with id<{wallet.owner_id}> already has 3 wallets."
        message = {"message": err_msg}
        content = {"error": message}
        return JSONResponse(
            status_code=409,
            content=content,
        )
    result = {"wallet_id": wallet.wallet_id, "balance_btc": 1, "balance_usd": 42316.90}
    return {"wallet": result}


@wallet_api.get("/wallet/{wallet_id}", status_code=200, response_model=WalletResp)
def get_wallet(wallet_id: UUID, wallets: WalletDep) -> dict[str, Any] | JSONResponse:
    try:
        wallet = wallets.read_with_wallet_id(wallet_id)
        result = {
            "wallet_id": wallet.wallet_id,
            "balance_btc": wallet.balance,
            "balance_usd": wallet.balance * 42316.90,
        }
        return {"wallet": result}
    except DoesNotExistError:
        message = {"message": f"Wallet with id<{wallet_id}> does not exist."}
        content = {"error": message}
        return JSONResponse(
            status_code=404,
            content=content,
        )


@wallet_api.get(
    "/wallets/{address}/transactions", status_code=200, response_model=TransacListResp
)
def get_wallet_transactions(
    wallet_id: UUID, wallets: WalletDep
) -> dict[str, Any] | JSONResponse:
    try:
        # transactions = wallets.get_all_transactions(wallet_id)
        # return {"transactions": transactions}
        pass
    except DoesNotExistError:
        message = {"message": f"Wallet with id<{wallet_id}> does not exist."}
        content = {"error": message}
        return JSONResponse(
            status_code=404,
            content=content,
        )
