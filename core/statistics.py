from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


class StatisticsProtocol(Protocol):
    def get_number_of_transactions(self) -> int:
        pass

    def get_bitcoin_profit(self) -> float:
        pass


@dataclass
class Statistics:
    number_of_transactions: int
    bitcoin_profit: float

    def get_number_of_transactions(self) -> int:
        return self.number_of_transactions

    def get_bitcoin_profit(self) -> float:
        return self.bitcoin_profit


class StatisticsRepository(Protocol):
    def read(self, admin_key: UUID) -> StatisticsProtocol:
        pass
