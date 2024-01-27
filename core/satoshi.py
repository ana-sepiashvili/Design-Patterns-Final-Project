from dataclasses import dataclass


@dataclass
class Satoshi:
    amount: int

    def get_amount(self) -> int:
        return self.amount
