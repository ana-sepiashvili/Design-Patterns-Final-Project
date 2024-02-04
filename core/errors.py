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
    type: str

    def get_id(self) -> str:
        return self.id

    def get_type(self) -> str:
        return self.type


class SameWalletTransactionError(Exception):
    pass


class ConverterError(Exception):
    @staticmethod
    def get_error_message() -> str:
        return "converter has met an error"


@dataclass
class WrongOwnerError(Exception):
    owner_id: str
    wallet_id: str

    def get_owner_id(self) -> str:
        return self.owner_id

    def get_wallet_id(self) -> str:
        return self.wallet_id


class NoAccessError(Exception):
    pass
