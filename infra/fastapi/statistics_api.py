from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import NoAccessError
from infra.fastapi.dependables import TransactionRepositoryDependable

statistics_api = APIRouter(tags=["Statistics"])


class StatisticsItem(BaseModel):
    number_of_transactions: int
    bitcoin_profit: float


class StatisticsItemEnvelope(BaseModel):
    statistics: StatisticsItem


@statistics_api.get(
    "/statistics/{user_id}",
    status_code=200,
    response_model=StatisticsItemEnvelope,
)
def get_statistics(
    user_id: UUID, transactions: TransactionRepositoryDependable
) -> dict[str, Any] | JSONResponse:
    try:
        statistics = transactions.read_statistics(user_id)
        return {"statistics": statistics}
    except NoAccessError:
        return JSONResponse(
            status_code=403,
            content={"message": f"User with id<{user_id}> does not have admin access."},
        )
