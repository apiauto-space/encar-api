"""Encar clients: the apiauto clients with the market preset to ``kr``."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Sequence
from datetime import datetime
from decimal import Decimal
from types import TracebackType
from typing import TYPE_CHECKING, Any, Literal

import apiauto
from apiauto import (
    Car,
    CarsPage,
    Change,
    ChangesPage,
    ChangeType,
    Dictionaries,
    Market,
    ReferenceItem,
    Usage,
)

if TYPE_CHECKING:
    import httpx
    from apiauto import CarFilters
    from typing_extensions import Self, Unpack

MARKET: Literal["kr"] = "kr"
"""The apiauto.space market of Encar."""
SOURCE: Literal["encar"] = "encar"
"""The ``source`` of every record this package returns."""
SHARED_MARKET = False
"""``True`` when the market also holds another source and records are filtered on the client."""


def car_id(listing: str | int) -> str:
    """The full record id for a Encar listing number: ``42793038`` -> ``encar:42793038``.

    An id that already has the ``encar:`` prefix is returned as is; another
    source's prefix raises ``ValueError``.
    """
    text = str(listing).strip()
    if not text:
        raise ValueError("listing must not be empty")
    prefix, sep, number = text.partition(":")
    if not sep:
        return f"{SOURCE}:{text}"
    if prefix != SOURCE or not number:
        raise ValueError(f"not a Encar id: {text!r}")
    return text


def _ours(car: Car) -> bool:
    return car.get("source") == SOURCE


def _our_change(change: Change) -> bool:
    return change["car_id"].startswith(SOURCE + ":")


def _core_options(base_url: str | None) -> dict[str, Any]:
    return {} if base_url is None else {"base_url": base_url}


def _own_market(markets: list[Market]) -> Market:
    for market in markets:
        if market["market"] == MARKET:
            return market
    raise apiauto.ApiautoError(f"the API did not list the {MARKET} market")


class Client:
    """Encar client of the apiauto.space API, synchronous.

    Args:
        api_key: Your key; defaults to the ``APIAUTO_KEY`` environment variable.
        base_url: The API root; ``https://api.apiauto.space/v1`` when omitted.
        timeout: Seconds to wait for a response.
        max_retries: Retries after 429, 5xx or a network error.
        http_client: Your own ``httpx.Client``; the client does not close it.

    Use it as a context manager or call :meth:`close`::

        with encar_api.Client() as client:
            page = client.cars(brand="Hyundai", limit=20)

    The general client is available as :attr:`core` for anything this one does not wrap.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.core = apiauto.Client(
            api_key,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
            **_core_options(base_url),
        )

    def close(self) -> None:
        """Close the HTTP connections (unless the ``http_client`` was yours)."""
        self.core.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()

    def cars(self, **filters: Unpack[CarFilters]) -> CarsPage:
        """One page of Encar cars: ``GET /cars?market=kr``.

        Takes the filters of :meth:`apiauto.Client.cars`: ``brand``, ``model``, ``year_min``,
        ``year_max``, ``price_min``, ``price_max`` (in KRW), ``mileage_max``, ``sort``,
        ``limit``, ``cursor`` and more. Every car returned counts against the quota.
        """
        page = self.core.cars(MARKET, **filters)
        return page

    def iter_cars(self, *, max_items: int | None = None, **filters: Unpack[CarFilters]) -> Iterator[Car]:
        """Every Encar car matching the filters, following ``next_cursor``.

        Args:
            max_items: Stop after this many cars.
            **filters: The filters of :meth:`cars`; ``limit`` sets the page size.
        """
        yield from self.core.iter_cars(MARKET, max_items=max_items, **filters)

    def car(self, listing: str | int) -> Car:
        """One car by listing number (``42793038``) or record id (``encar:42793038``).

        Cars taken off sale stay available for 14 days with ``is_active=False``.
        """
        return self.core.car(car_id(listing))

    def changes(
        self,
        since: datetime | str,
        *,
        type: ChangeType | Sequence[ChangeType] | None = None,  # noqa: A002
        min_pct: float | Decimal | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ChangesPage:
        """One page of the change feed: new cars, cars taken off sale and price changes since a moment."""
        page = self.core.changes(MARKET, since, type=type, min_pct=min_pct, limit=limit, cursor=cursor)
        return page

    def iter_changes(
        self,
        since: datetime | str,
        *,
        type: ChangeType | Sequence[ChangeType] | None = None,  # noqa: A002
        min_pct: float | Decimal | None = None,
        limit: int | None = None,
        max_items: int | None = None,
    ) -> Iterator[Change]:
        """Every event of the change feed since a moment, following ``next_cursor``."""
        yield from self.core.iter_changes(
            MARKET, since, type=type, min_pct=min_pct, limit=limit, max_items=max_items
        )

    def brands(self) -> list[ReferenceItem]:
        """Makes of the kr market with car counts, most frequent first. Free."""
        return self.core.brands(MARKET)

    def models(self, brand: str) -> list[ReferenceItem]:
        """Models of a make with car counts. Free."""
        return self.core.models(MARKET, brand)

    def dictionaries(self) -> Dictionaries:
        """Canonical values of ``fuel``, ``transmission``, ``body_type`` and more. Free."""
        return self.core.dictionaries()

    def status(self) -> Market:
        """The kr market: plan access, data age and the number of active cars. Free."""
        return _own_market(self.core.markets())

    def usage(self) -> Usage:
        """The plan, its term and how much of the quota is spent. Free."""
        return self.core.usage()


class AsyncClient:
    """Encar client of the apiauto.space API for asyncio; the methods of :class:`Client`.

    ::

        async with encar_api.AsyncClient() as client:
            page = await client.cars(brand="Hyundai", limit=20)
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.core = apiauto.AsyncClient(
            api_key,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
            **_core_options(base_url),
        )

    async def close(self) -> None:
        """Close the HTTP connections (unless the ``http_client`` was yours)."""
        await self.core.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def cars(self, **filters: Unpack[CarFilters]) -> CarsPage:
        """One page of Encar cars; see :meth:`Client.cars`."""
        page = await self.core.cars(MARKET, **filters)
        return page

    async def iter_cars(
        self, *, max_items: int | None = None, **filters: Unpack[CarFilters]
    ) -> AsyncIterator[Car]:
        """Every Encar car matching the filters; see :meth:`Client.iter_cars`."""
        async for car in self.core.iter_cars(MARKET, max_items=max_items, **filters):
            yield car

    async def car(self, listing: str | int) -> Car:
        """One car by listing number or record id; see :meth:`Client.car`."""
        return await self.core.car(car_id(listing))

    async def changes(
        self,
        since: datetime | str,
        *,
        type: ChangeType | Sequence[ChangeType] | None = None,  # noqa: A002
        min_pct: float | Decimal | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ChangesPage:
        """One page of the change feed; see :meth:`Client.changes`."""
        page = await self.core.changes(MARKET, since, type=type, min_pct=min_pct, limit=limit, cursor=cursor)
        return page

    async def brands(self) -> list[ReferenceItem]:
        """Makes of the kr market with car counts. Free."""
        return await self.core.brands(MARKET)

    async def models(self, brand: str) -> list[ReferenceItem]:
        """Models of a make with car counts. Free."""
        return await self.core.models(MARKET, brand)

    async def dictionaries(self) -> Dictionaries:
        """Canonical values of ``fuel``, ``transmission``, ``body_type`` and more. Free."""
        return await self.core.dictionaries()

    async def status(self) -> Market:
        """The kr market: plan access, data age and the number of active cars. Free."""
        return _own_market(await self.core.markets())

    async def usage(self) -> Usage:
        """The plan, its term and how much of the quota is spent. Free."""
        return await self.core.usage()
