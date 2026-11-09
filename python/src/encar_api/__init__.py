"""Encar API client for Python: South Korean used-car listings from Encar as JSON.

A thin layer over the apiauto.space client (``apiauto``) with the market preset::

    import encar_api

    with encar_api.Client() as client:  # the key comes from APIAUTO_KEY
        for car in client.cars(brand="Hyundai", year_min=2020, limit=20)["items"]:
            print(car["id"], car["title"], car["price"]["amount"])

From the apiauto.space team. Not affiliated with Encar or SK Encar.
"""

from apiauto import (
    ApiautoError,
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    Car,
    CarFilters,
    CarsPage,
    Change,
    ChangesPage,
    ChangeType,
    Market,
    NotFoundError,
    PermissionDeniedError,
    Price,
    QuotaExceededError,
    RateLimitError,
    ReferenceItem,
    ServerError,
    ServiceUnavailableError,
    Usage,
)

from ._client import MARKET, SHARED_MARKET, SOURCE, AsyncClient, Client, car_id
from ._version import __version__
from .types import EncarRaw, FxQuote, raw

__all__ = [
    "MARKET",
    "SHARED_MARKET",
    "SOURCE",
    "APIConnectionError",
    "ApiautoError",
    "AsyncClient",
    "AuthenticationError",
    "BadRequestError",
    "Car",
    "CarFilters",
    "CarsPage",
    "Change",
    "ChangeType",
    "ChangesPage",
    "Client",
    "EncarRaw",
    "FxQuote",
    "Market",
    "NotFoundError",
    "PermissionDeniedError",
    "Price",
    "QuotaExceededError",
    "RateLimitError",
    "ReferenceItem",
    "ServerError",
    "ServiceUnavailableError",
    "Usage",
    "__version__",
    "car_id",
    "raw",
]
