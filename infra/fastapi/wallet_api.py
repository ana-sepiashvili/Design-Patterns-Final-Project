from typing import Any
from uuid import UUID

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.constants import WALLET_LIMIT
from core.errors import (
    ConverterError,
    DoesNotExistError,
    ThreeWalletsError,
    WrongOwnerError,
)
from core.wallet import Wallet
from infra.converter import btc_to_usd
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
        result = {
            "wallet_id": str(wallet.get_id()),
            "balance_btc": wallet.get_bitcoin_balance(),
            "balance_usd": btc_to_usd(wallet.get_bitcoin_balance()),
        }
        return {"wallet": result}
    except ThreeWalletsError:
        err_msg = f"User with id<{api_key}> already has {WALLET_LIMIT} wallets."
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

    except ConverterError as e:
        message = {"message": e.get_error_message()}
        content = {"error": message}
        return JSONResponse(
            status_code=599,
            content=content,
        )


@wallet_api.get("/wallets/{address}", status_code=200, response_model=WalletResp)
def get_wallet(
    address: UUID,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    try:
        users.read(api_key)
        wallet = wallets.read_with_wallet_id(address)
        wallets.wallet_belongs_to_owner(api_key, address)
        result = {
            "wallet_id": str(wallet.get_id()),
            "balance_btc": wallet.get_bitcoin_balance(),
            "balance_usd": btc_to_usd(wallet.get_bitcoin_balance()),
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
        message = {
            "message": f"User with id<{e.get_owner_id()}> doesn't "
            f"own wallet with id<{e.get_wallet_id()}>"
        }
        content = {"error": message}
        return JSONResponse(
            status_code=400,
            content=content,
        )

    except ConverterError as e:
        message = {"message": e.get_error_message()}
        content = {"error": message}
        return JSONResponse(
            status_code=599,
            content=content,
        )


@wallet_api.get(
    "/wallets/{address}/transactions",
    status_code=200,
    response_model=TransactionListResp,
)
def get_wallet_transactions(
    address: UUID,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    transactions: TransactionRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    result = []
    try:
        users.read(api_key)
        wallets.wallet_belongs_to_owner(api_key, address)
        wallets.read_with_wallet_id(address)
        transactions_list = transactions.read_wallet_transactions(address)
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
        message = {
            "message": f"User with id<{e.get_owner_id()}> doesn't "
            f"own wallet with id<{e.get_wallet_id()}>"
        }
        content = {"error": message}
        return JSONResponse(
            status_code=400,
            content=content,
        )

    except ConverterError as e:
        message = {"message": e.get_error_message()}
        content = {"error": message}
        return JSONResponse(
            status_code=599,
            content=content,
        )
