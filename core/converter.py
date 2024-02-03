import requests

from core.errors import ConverterError
from runner.constants import BTC_TO_SAT, CONVERSION_API_LINK


def btc_to_usd(btc: float) -> float:
    url = CONVERSION_API_LINK
    params = {"ids": "bitcoin", "vs_currencies": "usd"}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        btc_to_usd_rate: float = response.json()["bitcoin"]["usd"]
        return btc * btc_to_usd_rate
    else:
        raise ConverterError


def btc_to_sat(btc: float) -> int:
    return round(btc * BTC_TO_SAT)
