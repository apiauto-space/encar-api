# Encar API clients for Python and JavaScript

South Korean used-car listings from Encar as clean JSON through the [apiauto.space](https://apiauto.space/en/encar-api/) REST API: search by
make, model, year, price and mileage, fetch one listing by its number, follow new cars and price changes.
No scraper to write or maintain.

| Language | Package | Install | Folder |
|---|---|---|---|
| Python 3.10+ | [`encar-api-client` on PyPI](https://pypi.org/project/encar-api-client/) | `pip install encar-api-client` | [python/](python/) |
| JavaScript / TypeScript | [`encar-api-client` on npm](https://www.npmjs.com/package/encar-api-client) | `npm install encar-api-client` | [js/](js/) |

```python
import encar_api

with encar_api.Client() as client:  # reads APIAUTO_KEY
    for car in client.iter_cars(max_items=20, brand="Hyundai", year_min=2020):
        print(car["id"], car["title"], car["price"]["amount"])
```

```ts
import { EncarApi } from "encar-api-client";

for await (const car of new EncarApi().iterCars({ brand: "Hyundai", year_min: 2020, maxItems: 20 })) {
  console.log(car.id, car.title, car.price.amount);
}
```

Both are thin layers over the general apiauto.space clients ([Python](https://github.com/apiauto-space/apiauto-python),
[JavaScript](https://github.com/apiauto-space/apiauto-js)) with the market preset to `kr`. A key comes
from the Telegram bot [@apiautospace_bot](https://t.me/apiautospace_bot?start=demo); see each package's README.

More: [Encar API page](https://apiauto.space/en/encar-api/), [API documentation](https://apiauto.space/en/docs/),
[examples in curl, Python, JavaScript and PHP](https://github.com/apiauto-space/encar-api-examples). Clients for
the other sources: [encar-api](https://github.com/apiauto-space/encar-api),
[che168-api](https://github.com/apiauto-space/che168-api), [copart-api](https://github.com/apiauto-space/copart-api),
[iaai-api](https://github.com/apiauto-space/iaai-api).

From the apiauto.space team. Not affiliated with Encar or SK Encar; Encar is a trademark of its owner and is
named here only to say which listings the clients return. MIT license.
