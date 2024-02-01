from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from core.errors import DoesNotExistError, ExistsError
from core.transaction import Transaction

transaction_api = APIRouter(tags=["Transactions"])


class MakeTransactionRequest(BaseModel):
    transaction_id: UUID
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
    units: UnitRepositoryDependable,
) -> dict[str, Any] | JSONResponse:
    transaction = Transaction(**request.model_dump())
    try:
        units.read(transaction.get_unit_id())
        try:
            transactions.add(transaction)
            return {"product": transaction}
        except ExistsError:
            return JSONResponse(
                status_code=409,
                content={
                    "error": {
                        "message": f"Product with "
                        f"barcode<{transaction.get_barcode()}> already exists."
                    }
                },
            )
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "message": f"Unit with id<{transaction.get_unit_id()}> does not exist."
                }
            },
        )


@product_api.get(
    "/products/{product_id}", status_code=200, response_model=UserItemEnvelope
)
def read_product(
    product_id: UUID, products: ProductRepositoryDependable
) -> dict[str, Product] | JSONResponse:
    try:
        product = products.read(product_id)
        return {"product": product}
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {"message": f"Product with id<{product_id}> does not exist."}
            },
        )


@product_api.get("/products", status_code=200, response_model=ProductListEnvelope)
def read_all(products: ProductRepositoryDependable) -> dict[str, Any]:
    return {"products": products.read_all()}


@product_api.patch("/products/{product_id}", status_code=200, response_model=Dict)
def update_product(
    product_id: UUID,
    request: UpdateProductRequest,
    products: ProductRepositoryDependable,
) -> dict[str, Any] | JSONResponse:
    try:
        products.update(product_id, **request.model_dump())
        return {}
    except DoesNotExistError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {"message": f"Product with id<{product_id}> does not exist."}
            },
        )
