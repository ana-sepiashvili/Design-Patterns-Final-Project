from typing import Any
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from core.errors import DoesNotExistError
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
    amount: float


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
    products: list[TransactionItem]


@transaction_api.post(
    "/transactions", status_code=201, response_model=TransactionItemEnvelope
)
def make_transaction(
    request: MakeTransactionRequest,
    transactions: TransactionRepositoryDependable,
    wallets: WalletRepositoryDependable,
) -> dict[str, Any] | JSONResponse:
    print("SEEEEEEEEEEEEEEEEEEEEEE")
    args = request.model_dump()
    print(args)
    if wallets.has_same_owner(args["from_id"], args["to_id"]):
        transaction = Transaction(**request.model_dump())
    else:
        transaction = Transaction(
            args["from_id"],
            args["to_id"],
            args["amount"] * (1 - TRANSACTION_FEE),
            args["amount"] * TRANSACTION_FEE,
        )
    try:
        transactions.add(transaction)
        wallets.make_transaction(transaction)
        return {"transaction": transaction}
    except DoesNotExistError as e:
        return JSONResponse(
            status_code=404,
            content={
                "error": {"message": f"Walled with id<{e.get_id()}> does not exist."}
            },
        )


@transaction_api.get(
    "/transactions", status_code=200, response_model=TransactionListEnvelope
)
def read_user_transactions(
    request: ReadUserTransactionsRequest,
    transactions: TransactionRepositoryDependable,
    users: UserRepositoryDependable,
) -> dict[str, Any] | JSONResponse:
    try:
        users.read(**request.model_dump())
        return {
            "transactions": transactions.read_user_transactions(**request.model_dump())
        }
    except DoesNotExistError as e:
        return JSONResponse(
            status_code=404,
            content={
                "error": {"message": f"User with id<{e.get_id()}> does not exist."}
            },
        )
