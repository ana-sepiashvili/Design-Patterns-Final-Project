import requests

from core.constants import CONVERSION_API_LINK
from core.errors import ConverterError


def btc_to_usd(btc: float) -> float:
    url = CONVERSION_API_LINK

    response = requests.get(url, params=None)
    if response.status_code == 200:
        rate: float = response.json()["USD"]["last"]
        return btc * rate
    else:
        raise ConverterError
