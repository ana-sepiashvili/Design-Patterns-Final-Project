from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.errors import DoesNotExistError, ExistsError
from core.user import User
from infra.fastapi.dependables import UserRepositoryDependable

user_api = APIRouter(tags=["Users"])


class RegisterUserRequest(BaseModel):
    email: str


class UserItem(BaseModel):
    id: UUID
    email: str


class UserItemEnvelope(BaseModel):
    user: UserItem


@user_api.post(
    "/users",
    status_code=201,
    response_model=UserItemEnvelope,
)
def register(
    request: RegisterUserRequest, users: UserRepositoryDependable
) -> dict[str, User] | JSONResponse:
    user = User(**request.model_dump())
    user_email = user.get_email()
    try:
        users.add(user)
        return {"user": user}
    except ExistsError:
        return JSONResponse(
            status_code=409,
            content={"message": f"User with email<{user_email}> already exists."},
        )
