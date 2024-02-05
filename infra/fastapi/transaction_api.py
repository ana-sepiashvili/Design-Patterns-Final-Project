from typing import Any
from uuid import UUID

from fastapi import APIRouter, Header
from pydantic import BaseModel
from starlette.responses import JSONResponse

from core.errors import DoesNotExistError, SameWalletTransactionError, WrongOwnerError
from infra.fastapi.dependables import (
    TransactionRepositoryDependable,
    UserRepositoryDependable,
    WalletRepositoryDependable,
)
from infra.transaction_factory import TransactionFactory

transaction_api = APIRouter(tags=["Transactions"])


class MakeTransactionRequest(BaseModel):
    from_id: str
    to_id: str
    bitcoin_amount: float


class ReadUserTransactionsRequest(BaseModel):
    user_id: UUID


class UpdateProductRequest(BaseModel):
    price: int


class TransactionItem(BaseModel):
    id: UUID
    from_id: UUID
    to_id: UUID
    bitcoin_amount: float
    bitcoin_fee: float


class TransactionItemEnvelope(BaseModel):
    transaction: TransactionItem


class TransactionListEnvelope(BaseModel):
    transactions: list[TransactionItem]


@transaction_api.post(
    "/transactions", status_code=201, response_model=TransactionItemEnvelope
)
def make_transaction(
    request: MakeTransactionRequest,
    transactions: TransactionRepositoryDependable,
    wallets: WalletRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    args = request.model_dump()
    try:
        users.read(api_key)
        wallets.wallet_belongs_to_owner(api_key, args["from_id"])
        transaction_factory = TransactionFactory(wallets)
        transaction = transaction_factory.create_transaction(
            args["from_id"], args["to_id"], args["bitcoin_amount"]
        )
        wallets.make_transaction(transaction)
        try:
            transactions.add(transaction)
            return {"transaction": transaction}
        except SameWalletTransactionError:
            wallet_id = args["from_id"]
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "message": f"You cannot transfer from wallet"
                        f" with id<{wallet_id}> to itself."
                    }
                },
            )

    except DoesNotExistError as e:
        message = {"message": f"{e.get_type()} with id<{e.get_id()}> does not exist."}
        content = {"error": message}
        return JSONResponse(
            status_code=404,
            content=content,
        )

    except WrongOwnerError as we:
        message = {
            "message": f"User with id<{we.get_owner_id()}> doesn't "
            f"own wallet with id<{we.get_wallet_id()}>"
        }
        content = {"error": message}
        return JSONResponse(
            status_code=400,
            content=content,
        )


@transaction_api.get(
    "/transactions", status_code=200, response_model=TransactionListEnvelope
)
def read_user_transactions(
    wallets: WalletRepositoryDependable,
    transactions: TransactionRepositoryDependable,
    users: UserRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> dict[str, Any] | JSONResponse:
    try:
        users.read(api_key)
        wallets_list = wallets.read_with_user_id(api_key)
        result = []
        for wallet in wallets_list:
            result.extend(transactions.read_wallet_transactions(wallet.get_id()))
        return {"transactions": result}
    except DoesNotExistError as e:
        return JSONResponse(
            status_code=404,
            content={
                "error": {"message": f"User with id<{e.get_id()}> does not exist."}
            },
        )
