# encar-api — Encar API client for JavaScript and TypeScript

[![npm version](https://img.shields.io/npm/v/encar-api.svg)](https://www.npmjs.com/package/encar-api)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/apiauto-space/encar-api/blob/main/LICENSE)

`encar-api` gives you South Korean used-car listings from Encar as clean JSON through the [apiauto.space](https://apiauto.space/en/encar-api/)
REST API, without writing or maintaining a scraper. Search by make, model, year, price and mileage, page
through the whole catalog, fetch one listing by its number and follow a feed of new cars, cars taken off sale
and price changes.

It is a thin layer over the general [`apiauto`](https://www.npmjs.com/package/apiauto) client with the market
preset to `kr`, plus types for the Encar-only fields. It comes from the apiauto.space team; the project
is not affiliated with Encar or SK Encar.

- One class, `EncarApi`, ESM, TypeScript types, the only dependency is `apiauto` (which has none)
- `car("42793038")` takes the Encar listing number as well as the record id
- `EncarRaw` types for the Encar-only fields in `car.raw`
- Node 20.19+, Bun, Deno and edge runtimes with `fetch`

## Install

```bash
npm install encar-api
```

## Get a key

Open the Telegram bot [@apiautospace_bot](https://t.me/apiautospace_bot?start=demo) and take a free demo
key: one day, 100 data requests, up to 20 cars per request. Paid plans are on the
[pricing page](https://apiauto.space/en/#pricing).

Save the key in the `APIAUTO_KEY` environment variable — the client reads it from there. Keep the key on your
server: the API does not accept browser requests, and a key in page code is visible to every visitor.

## Quick start

```ts
import { EncarApi } from "encar-api";

const api = new EncarApi(); // reads APIAUTO_KEY

const page = await api.cars({ brand: "Hyundai", year_min: 2020, limit: 20 });
for (const car of page.items) {
  console.log(car.id, car.title, car.price.amount, car.price.currency);
}

const one = await api.car("42793038"); // a listing number or "encar:42793038"
console.log(one.listing_url, one.photos[0]);
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
`null`. Prices are decimal strings in KRW, `price_usd` is converted at the ECB daily rate.

## Methods

| Method | What it does | Quota |
|---|---|---|
| `cars(filters)` | One page of Encar cars: `brand`, `model`, `year_min`, `year_max`, `price_min`, `price_max`, `mileage_max`, `fuel`, `body_type`, `sort`, `limit`, `cursor` | Cars returned |
| `iterCars({ ...filters, maxItems })` | Every matching car, page after page | Cars returned |
| `car(listing)` | One car by listing number or id, including cars taken off sale in the last 14 days | 1 record |
| `changes({ since, type })` / `iterChanges(...)` | Feed of `added`, `disappeared`, `price_drop`, `price_up` events | Events returned |
| `brands()` / `models(brand)` | Makes and models with car counts | Free |
| `status()` | Plan access, data age and the number of active cars of the market | Free |
| `usage()` | Your plan, its term and the quota spent | Free |

The general client is at `api.core` for anything else. Errors are the `apiauto` error classes, re-exported
here: `QuotaExceededError`, `RateLimitError`, `NotFoundError`, `AuthenticationError` and the rest.

## Encar-only fields

```ts
import { raw } from "encar-api";

const extra = raw(car); // typed as EncarRaw
console.log(extra.source_values);
```

## Links

- [Encar API on apiauto.space](https://apiauto.space/en/encar-api/) and the [API documentation](https://apiauto.space/en/docs/)
- [`apiauto`](https://www.npmjs.com/package/apiauto): the general client for all markets
- Clients for the other sources: [`encar-api`](https://www.npmjs.com/package/encar-api),
  [`che168-api`](https://www.npmjs.com/package/che168-api), [`copart-api`](https://www.npmjs.com/package/copart-api),
  [`iaai-api`](https://www.npmjs.com/package/iaai-api)
- [Examples in curl, Python, JavaScript and PHP](https://github.com/apiauto-space/encar-api-examples)
- The Python version of this client: [`encar-api` on PyPI](https://pypi.org/project/encar-api/)

## License

MIT. Encar is a trademark of its owner; it is named here only to say which listings the client returns.
