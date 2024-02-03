from dataclasses import dataclass
from typing import Protocol

import requests

from core.errors import ConverterError
from runner.constants import BTC_TO_SAT, CONVERSION_API_LINK


class ConverterProtocol(Protocol):
    def btc_to_usd(self) -> float:
        pass

    def btc_to_sat(self) -> int:
        pass


@dataclass
class Converter:
    btc: float

    def btc_to_usd(self) -> float:
        url = CONVERSION_API_LINK
        params = {"ids": "bitcoin", "vs_currencies": "usd"}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            btc_to_usd_rate: float = response.json()["bitcoin"]["usd"]
            return self.btc * btc_to_usd_rate
        else:
            raise ConverterError

    def btc_to_sat(self) -> int:
        return round(self.btc * BTC_TO_SAT)
