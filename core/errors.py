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


# class NoTransactionsError(Exception):
#     id: str
#
#     def get_id(self) -> str:
#         return self.id


class ConverterError(Exception):
    def get_err_msg(self) -> str:
        return "converter has met an error"


@dataclass
class WrongOwnerError(Exception):
    owner_id: str
    wallet_id: str

    def get_err_msg(self) -> str:
        return (
            f"User with id<{self.owner_id}> doesn't "
            f"own wallet with id<{self.wallet_id}>"
        )


class NoAccessError(Exception):
    pass
