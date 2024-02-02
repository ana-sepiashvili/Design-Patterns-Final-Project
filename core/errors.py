from dataclasses import dataclass


class ThreeWalletsError(Exception):
    pass


class ExistsError(Exception):
    pass


class NotEnoughMoneyError(Exception):
    pass


@dataclass
class DoesNotExistError(Exception):
    id: str

    def get_id(self) -> str:
        return self.id


class SameWalletTransactionError(Exception):
    pass


class NoTransactionsError(Exception):
    id: str

    def get_id(self) -> str:
        return self.id
