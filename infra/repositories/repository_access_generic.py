from typing import TypeVar, Protocol

T = TypeVar("T")


class RepositoryAccess(Protocol[T]):
    def __init__(self) -> None:
        pass

    def execute_query(self, query: None | T) -> list[T]:
        pass

    def execute_update(self, update: T) -> None:
        pass

    def execute_insert(self, insert: T) -> None:
        pass

    def execute_side_query(self, query: None | T) -> list[T]:
        pass
