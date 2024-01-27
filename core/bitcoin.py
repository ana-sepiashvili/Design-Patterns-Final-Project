from dataclasses import dataclass


@dataclass
class Bitcoin:
    amount: float

    def get_amount(self) -> float:
        return self.amount
