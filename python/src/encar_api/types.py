"""Types of the Encar-only fields of a record.

Every record has the same common keys in every market (see :class:`apiauto.Car`);
the fields only Encar has are in ``car["raw"]``. :func:`raw` returns them typed::

    from encar_api import raw

    extra = raw(car)
    print(extra.get("source_values"))
"""

from __future__ import annotations

from typing import TypedDict, cast

from apiauto import Car

__all__ = ["EncarRaw", "FxQuote", "raw"]


class FxQuote(TypedDict):
    """The ECB daily rate behind ``price_usd``."""

    currency: str
    usd_per_unit: str
    """Decimal string: US dollars for one unit of ``currency``."""
    date: str
    source: str


class EncarRaw(TypedDict, total=False):
    """Encar-only fields of a record (``car["raw"]``). Keys can be missing; read them with ``.get``."""

    badge: str | None
    """Encar's badge (trim) in Korean, as the listing shows it."""
    badge_detail: str | None
    office_city: str | None
    """The dealer's province in Korean, for example ``경기``."""
    sell_type: str | None
    """``normal``, ``lease`` or ``rental``: lease and rental listings show a monthly payment, not a price."""
    has_vin: bool
    form_year: str | None
    """The model-year code, ``YYYYMM``."""
    body_class: str | None
    condition: list[str]
    trust: list[str]
    service_mark: list[str]
    source_values: dict[str, str | None]
    """Encar's own Korean spellings of make, model, trim, fuel and region."""
    fx: FxQuote | None


def raw(car: Car) -> EncarRaw:
    """The Encar-only fields of a record, typed as :class:`EncarRaw`."""
    return cast(EncarRaw, car.get("raw") or {})
