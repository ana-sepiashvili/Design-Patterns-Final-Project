from dataclasses import dataclass


@dataclass
class Statistics:
    number_of_transactions: int
    bitcoin_profit: float

    def get_number_of_transactions(self) -> int:
        return self.number_of_transactions

    def get_bitcoin_profit(self) -> float:
        return self.bitcoin_profit
