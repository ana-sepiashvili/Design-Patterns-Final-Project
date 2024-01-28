from typing import Annotated

from fastapi import Depends
from fastapi.requests import Request

from infra.repositories.user_repository import UserRepository


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.users  # type: ignore


UserRepositoryDependable = Annotated[UserRepository, Depends(get_user_repository)]
