# encar-api-client — Encar API client for Python

[![PyPI version](https://img.shields.io/pypi/v/encar-api-client.svg)](https://pypi.org/project/encar-api-client/)
[![Python versions](https://img.shields.io/pypi/pyversions/encar-api-client.svg)](https://pypi.org/project/encar-api-client/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/apiauto-space/encar-api/blob/main/LICENSE)

`encar-api-client` gives you South Korean used-car listings from Encar as clean JSON through the [apiauto.space](https://apiauto.space/en/encar-api/)
REST API, without writing or maintaining a scraper. Search by make, model, year, price and mileage, page
through the whole catalog, fetch one listing by its number and follow a feed of new cars, cars taken off sale
and price changes.

It is a thin layer over the general [`apiauto-space`](https://pypi.org/project/apiauto-space/) client with
the market preset to `kr`, plus types for the Encar-only fields. It comes from the apiauto.space team;
the project is not affiliated with Encar or SK Encar.

- Sync `Client` and `AsyncClient`, retries on 429 and 5xx, one exception class per API error
- `car("42793038")` takes the Encar listing number as well as the record id
- `EncarRaw` types for the Encar-only fields in `car["raw"]`
- Python 3.10+, `py.typed`, checked with `mypy --strict`

## Install

```bash
pip install encar-api-client
```

The module you import is `encar_api`.

## Get a key

Open the Telegram bot [@apiautospace_bot](https://t.me/apiautospace_bot?start=demo) and take a free demo
key: one day, 100 data requests, up to 20 cars per request. Paid plans are on the
[pricing page](https://apiauto.space/en/#pricing).

Save the key in the `APIAUTO_KEY` environment variable — the client reads it from there:

```bash
export APIAUTO_KEY="your-key"
```

Keep the key on your server: the API does not accept browser requests.

## Quick start

```python
import encar_api

with encar_api.Client() as client:  # reads APIAUTO_KEY
    cars = list(client.iter_cars(max_items=20, brand="Hyundai", year_min=2020))
    for car in cars:
        print(car["id"], car["title"], car["price"]["amount"], car["price"]["currency"])

    # One car by its listing number, such as "42793038", or its id, such as "encar:42793038"
    one = client.car(cars[0]["source_id"])
    print(one["listing_url"], one["photos"][:1])
```

A record looks like this (shortened; real values from the catalog):

```json
{
  "id": "encar:42793038",
  "market": "kr",
  "source": "encar",
  "source_id": "42793038",
  "title": "2021 BMW 1 Series (F40) 118d M Sport",
  "brand": "BMW",
  "model": "1 Series (F40)",
  "year": 2021,
  "mileage_km": 122866,
  "fuel": "diesel",
  "transmission": null,
  "body_type": null,
  "price": {
    "amount": "17990000.00",
    "currency": "KRW"
  },
  "price_usd": "13265.53",
  "location": {
    "country": "KR",
    "region": "Gyeonggi",
    "city": null
  },
  "listing_url": "https://fem.encar.com/cars/detail/42793038",
  "is_active": true,
  "first_seen_at": "2026-09-23T11:36:05.145090Z",
  "photos": [
    "https://api.apiauto.space/img/encar:42793038/1.jpg?exp=...&sig=..."
  ],
  "raw": {
    "badge": "118d M 스포츠",
    "sell_type": "normal",
    "office_city": "경기",
    "form_year": "202110"
  }
}
```

Every record has the same keys as in the other apiauto.space markets; a value the source does not provide is
`None`. Prices are decimal strings in KRW, `price_usd` is converted at the ECB daily rate.

## Methods

| Method | What it does | Quota |
|---|---|---|
| `cars(**filters)` | One page of Encar cars: `brand`, `model`, `year_min`, `year_max`, `price_min`, `price_max`, `mileage_max`, `fuel`, `body_type`, `sort`, `limit`, `cursor` | Cars returned |
| `iter_cars(max_items=None, **filters)` | Every matching car, page after page | Cars returned |
| `car(listing)` | One car by listing number or id, including cars taken off sale in the last 14 days | 1 record |
| `changes(since, type=None)` / `iter_changes(...)` | Feed of `added`, `disappeared`, `price_drop`, `price_up` events | Events returned |
| `brands()` / `models(brand)` | Makes and models with car counts | Free |
| `status()` | Plan access, data age and the number of active cars of the market | Free |
| `usage()` | Your plan, its term and the quota spent | Free |

The general client is at `client.core` for anything else. Errors are the `apiauto` exceptions, re-exported
here: `QuotaExceededError`, `RateLimitError`, `NotFoundError`, `AuthenticationError` and the rest.

## Encar-only fields

```python
from encar_api import raw

extra = raw(car)  # typed as EncarRaw
print(extra.get("source_values"))
```

`EncarRaw` lists the keys with comments; every key is optional, so read them with `.get`.

## Links

- [Encar API on apiauto.space](https://apiauto.space/en/encar-api/) and the [API documentation](https://apiauto.space/en/docs/)
- [`apiauto-space`](https://pypi.org/project/apiauto-space/): the general client for all markets
- Clients for the other sources: [`che168-api`](https://pypi.org/project/che168-api/), [`copart-api`](https://pypi.org/project/copart-api/), [`iaai-api`](https://pypi.org/project/iaai-api/)
- [Examples in curl, Python, JavaScript and PHP](https://github.com/apiauto-space/encar-api-examples)
- The JavaScript version of this client: [`encar-api-client` on npm](https://www.npmjs.com/package/encar-api-client)

## License

MIT. Encar is a trademark of its owner; it is named here only to say which listings the client returns.
