from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.converter import btc_to_usd
from core.errors import DoesNotExistError, ThreeWalletsError
from core.wallet import Wallet
from infra.fastapi.dependables import (
    TransactionRepositoryDependable,
    UserRepositoryDependable,
    WalletRepositoryDependable,
)

wallet_api = APIRouter(tags=["Wallets"])


class CreateWalletReqt(BaseModel):
    owner_id: str


class WalletSingle(BaseModel):
    wallet_id: str
    balance_btc: float
    balance_usd: float


class WalletResp(BaseModel):
    wallet: WalletSingle


class TransactionItem(BaseModel):
    transaction_id: str
    from_id: str
    to_id: str
    bitcoin_amount: float
    bitcoin_fee: float


class TransactionListResp(BaseModel):
    transactions: list[TransactionItem]


@wallet_api.post("/wallets", status_code=201, response_model=WalletResp)
def create_wallet(
    request: CreateWalletReqt,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
) -> dict[str, Any] | JSONResponse:
    wallet = Wallet(**request.model_dump())
    try:
        users.read(wallet.get_owner_id())
        wallets.add(wallet)
    except ThreeWalletsError:
        err_msg = f"User with id<{wallet.get_owner_id()}> already has 3 wallets."
        message = {"message": err_msg}
        content = {"error": message}
        return JSONResponse(
            status_code=409,
            content=content,
        )
    except DoesNotExistError:
        err_msg = f"User with id<{wallet.get_owner_id()}> does not exist."
        message = {"message": err_msg}
        content = {"error": message}
        return JSONResponse(
            status_code=400,
            content=content,
        )
    result = {
        "wallet_id": str(wallet.get_id()),
        "balance_btc": wallet.get_balance(),
        "balance_usd": wallet.get_balance() * 42316.90,
    }
    return {"wallet": result}


@wallet_api.get("/wallets/{wallet_id}", status_code=200, response_model=WalletResp)
def get_wallet(
    wallet_id: UUID, wallets: WalletRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        wallet = wallets.read_with_wallet_id(wallet_id)
        print("EEEEEEEEEEEEE")
        print(btc_to_usd(1.0))
        result = {
            "wallet_id": str(wallet.get_id()),
            "balance_btc": wallet.get_balance(),
            "balance_usd": btc_to_usd(wallet.get_balance()),
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
    "/wallets/{wallet_id}/transactions",
    status_code=200,
    response_model=TransactionListResp,
)
def get_wallet_transactions(
    wallet_id: UUID,
    wallets: WalletRepositoryDependable,
    transactions: TransactionRepositoryDependable,
) -> dict[str, Any] | JSONResponse:
    try:
        wallets.read_with_wallet_id(wallet_id)
        transactions_list = transactions.read_wallet_transactions(wallet_id)
        result = []
        for transaction in transactions_list:
            result.append(
                {
                    "transaction_id": str(transaction.get_id()),
                    "from_id": str(transaction.get_from_id()),
                    "to_id": str(transaction.get_to_id()),
                    "bitcoin_amount": transaction.get_bitcoin_amount(),
                    "bitcoin_fee": transaction.get_bitcoin_fee(),
                }
            )
        return {"transactions": result}
    except DoesNotExistError as e:
        message = {"message": f"Wallet with id<{e.get_id()}> does not exist."}
        content = {"error": message}
        return JSONResponse(
            status_code=404,
            content=content,
        )
