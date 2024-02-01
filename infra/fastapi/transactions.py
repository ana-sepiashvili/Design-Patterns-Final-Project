from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from core.errors import DoesNotExistError, ExistsError
from core.transaction import Transaction
from infra.fastapi.dependables import TransactionRepositoryDependable, WalletDep

transaction_api = APIRouter(tags=["Transactions"])


class MakeTransactionRequest(BaseModel):
    from_id: UUID
    to_id: UUID
    amount: float


class UpdateProductRequest(BaseModel):
    price: int


class UserItem(BaseModel):
    id: UUID


class UserItemEnvelope(BaseModel):
    user: UserItem


class ProductListEnvelope(BaseModel):
    products: list[UserItem]


@transaction_api.post("/transactions", status_code=201, response_model=UserItemEnvelope)
def make_transaction(
    request: MakeTransactionRequest,
    transactions: TransactionRepositoryDependable,
    wallets: WalletDep,
) -> dict[str, Any] | JSONResponse:
    args = request.model_dump()
    if wallets.has_same_owner(args["from_id"], args["to_id"]):
        transaction = Transaction(**request.model_dump())
    else:
        transaction = Transaction(
            args["from_id"],
            args["to_id"],
            args["amount"] * 0.985,
            args["amount"] * 0.015,
        )
    try:
        transactions.add(transaction)
        wallets.make_transaction(transaction)
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "message": f"Walled with id<{args["from_id" an to_id]}> does not exist."
                }
            },
        )


# @product_api.get(
#     "/products/{product_id}", status_code=200, response_model=UserItemEnvelope
# )
# def read_product(
#     product_id: UUID, products: ProductRepositoryDependable
# ) -> dict[str, Product] | JSONResponse:
#     try:
#         product = products.read(product_id)
#         return {"product": product}
#     except DoesNotExistError:
#         return JSONResponse(
#             status_code=404,
#             content={
#                 "error": {"message": f"Product with id<{product_id}> does not exist."}
#             },
#         )
#
#
# @product_api.get("/products", status_code=200, response_model=ProductListEnvelope)
# def read_all(products: ProductRepositoryDependable) -> dict[str, Any]:
#     return {"products": products.read_all()}
#
#
# @product_api.patch("/products/{product_id}", status_code=200, response_model=Dict)
# def update_product(
#     product_id: UUID,
#     request: UpdateProductRequest,
#     products: ProductRepositoryDependable,
# ) -> dict[str, Any] | JSONResponse:
#     try:
#         products.update(product_id, **request.model_dump())
#         return {}
#     except DoesNotExistError:
#         return JSONResponse(
#             status_code=404,
#             content={
#                 "error": {"message": f"Product with id<{product_id}> does not exist."}
#             },
#         )
