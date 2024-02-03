from typing import Any
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from core.errors import DoesNotExistError, SameWalletTransactionError
from core.transaction import Transaction
from infra.fastapi.dependables import (
    TransactionRepositoryDependable,
    UserRepositoryDependable,
    WalletRepositoryDependable,
)
from runner.constants import TRANSACTION_FEE

transaction_api = APIRouter(tags=["Transactions"])


# test branch


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
) -> dict[str, Any] | JSONResponse:
    args = request.model_dump()
    try:
        if wallets.has_same_owner(args["from_id"], args["to_id"]):
            transaction = Transaction(**request.model_dump())
        else:
            transaction = Transaction(
                args["from_id"],
                args["to_id"],
                args["bitcoin_amount"] * (1 - TRANSACTION_FEE),
                args["bitcoin_amount"] * TRANSACTION_FEE,
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
        return JSONResponse(
            status_code=404,
            content={
                "error": {"message": f"Wallet with id<{e.get_id()}> does not exist."}
            },
        )


@transaction_api.get(
    "/transactions/{user_id}", status_code=200, response_model=TransactionListEnvelope
)
def read_user_transactions(
    user_id: UUID,
    wallets: WalletRepositoryDependable,
    transactions: TransactionRepositoryDependable,
    users: UserRepositoryDependable,
) -> dict[str, Any] | JSONResponse:
    try:
        users.read(user_id)
        wallets_list = wallets.read_with_user_id(user_id)
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
