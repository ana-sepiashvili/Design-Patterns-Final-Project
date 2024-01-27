from abc import ABC
from dataclasses import dataclass

# test2


@dataclass
class Currency(ABC):
    amount: float

    def get_amount(self) -> float:
        return self.amount


@dataclass
class Bitcoin(Currency):
    amount: float


@dataclass
class Satoshi(Currency):
    amount: float


@dataclass
class USD(Currency):
    amount: float
