from dataclasses import dataclass


@dataclass
class USD:
    amount: float

    def get_amount(self) -> float:
        return self.amount
