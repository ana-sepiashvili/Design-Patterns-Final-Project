from typing import Any
from uuid import UUID

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.converter import btc_to_usd
from core.errors import DoesNotExistError, ThreeWalletsError, WrongOwnerError
from core.wallet import Wallet
from infra.fastapi.dependables import (
    TransactionRepositoryDependable,
    UserRepositoryDependable,
    WalletRepositoryDependable,
)

wallet_api = APIRouter(tags=["Wallets"])


class WalletSingle(BaseModel):
    wallet_id: UUID
    balance_btc: float
    balance_usd: float


class WalletResp(BaseModel):
    wallet: WalletSingle


class TransactionItem(BaseModel):
    transaction_id: UUID
    from_id: UUID
    to_id: UUID
    bitcoin_amount: float
    bitcoin_fee: float


class TransactionListResp(BaseModel):
    transactions: list[TransactionItem]


@wallet_api.post("/wallets", status_code=201, response_model=WalletResp)
def create_wallet(
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    try:
        users.read(api_key)
        wallet = Wallet(owner_id=api_key)
        wallets.add(wallet)
    except ThreeWalletsError:
        err_msg = f"User with id<{api_key}> already has 3 wallets."
        message = {"message": err_msg}
        content = {"error": message}
        return JSONResponse(
            status_code=409,
            content=content,
        )
    except DoesNotExistError as e:
        err_msg = f"{e.get_type()} with id<{e.get_id()}> does not exist."
        message = {"message": err_msg}
        content = {"error": message}
        return JSONResponse(
            status_code=400,
            content=content,
        )
    result = {
        "wallet_id": str(wallet.get_id()),
        "balance_btc": wallet.get_balance(),
        "balance_usd": btc_to_usd(wallet.get_balance()),
    }
    return {"wallet": result}


@wallet_api.get("/wallets/{wallet_id}", status_code=200, response_model=WalletResp)
def get_wallet(
    wallet_id: UUID,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    try:
        users.read(api_key)
        wallet = wallets.read_with_wallet_id(wallet_id)
        wallets.wallet_belongs_to_owner(api_key, wallet_id)
        result = {
            "wallet_id": str(wallet.get_id()),
            "balance_btc": wallet.get_balance(),
            "balance_usd": btc_to_usd(wallet.get_balance()),
        }
        return {"wallet": result}
    except DoesNotExistError as e:
        message = {"message": f"{e.get_type()} with id<{e.get_id()}> does not exist."}
        content = {"error": message}
        return JSONResponse(
            status_code=404,
            content=content,
        )
    except WrongOwnerError as e:
        message = {"message": e.get_err_msg()}
        content = {"error": message}
        return JSONResponse(
            status_code=400,
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
    users: UserRepositoryDependable,
    transactions: TransactionRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    try:
        users.read(api_key)
        wallets.wallet_belongs_to_owner(api_key, wallet_id)
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
        message = {"message": f"{e.get_type()} with id<{e.get_id()}> does not exist."}
        content = {"error": message}
        return JSONResponse(
            status_code=404,
            content=content,
        )
    except WrongOwnerError as e:
        message = {"message": e.get_err_msg()}
        content = {"error": message}
        return JSONResponse(
            status_code=400,
            content=content,
        )
