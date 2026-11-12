// Unit tests against the compiled package (run `npm run build` first). fetch is mocked.
import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { EncarApi, MARKET, NotFoundError, SHARED_MARKET, SOURCE, VERSION, carId, raw } from "../dist/index.js";

const KEY = "test-key-0123456789abcdef";

/** A fetch that answers from a queue of JSON bodies (or `{ status, body }`) and records URLs. */
function mockFetch(queue) {
  const urls = [];
  const fetch = async (url) => {
    urls.push(new URL(url));
    const next = queue.shift();
    if (next === undefined) throw new Error(`unexpected request to ${url}`);
    const { status = 200, body = next } = next && next.__status ? { status: next.__status, body: next.body } : {};
    return new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
  };
  return { fetch, urls };
}

function setup(...queue) {
  const { fetch, urls } = mockFetch(queue);
  return { api: new EncarApi({ apiKey: KEY, fetch, maxRetries: 0 }), urls };
}

const car = (id) => ({ id, market: "kr", source: id.split(":")[0], title: `car ${id}`, raw: {} });
const page = (ids, next_cursor = null, count = null) => ({ items: ids.map(car), next_cursor, count });
const params = (url) => Object.fromEntries(url.searchParams);

describe("constants", () => {
  it("preset the market and source", () => {
    assert.equal(MARKET, "kr");
    assert.equal(SOURCE, "encar");
    assert.equal(SHARED_MARKET, false);
    assert.equal(VERSION, "0.1.1");
  });
});

describe("cars", () => {
  it("sends market=kr with the filters", async () => {
    const { api, urls } = setup(page(["encar:1"], null, 1));
    const result = await api.cars({ brand: "Hyundai", year_min: 2020, limit: 1 });
    assert.deepEqual(
      result.items.map((c) => c.id),
      ["encar:1"],
    );
    assert.equal(urls[0].pathname, "/v1/cars");
    assert.deepEqual(params(urls[0]), { market: "kr", brand: "Hyundai", year_min: "2020", limit: "1" });
  });

  it("does not let a filter override the market", async () => {
    const { api, urls } = setup(page([]));
    await api.cars({ market: "xx" });
    assert.equal(urls[0].searchParams.get("market"), "kr");
  });

  it("iterCars follows the cursor and caps the last page", async () => {
    const { api, urls } = setup(page(["encar:1", "encar:2"], "c2"), page(["encar:3"]));
    const ids = [];
    for await (const c of api.iterCars({ limit: 2, maxItems: 3 })) ids.push(c.id);
    assert.deepEqual(ids, ["encar:1", "encar:2", "encar:3"]);
    assert.equal(urls[1].searchParams.get("cursor"), "c2");
    assert.equal(urls[1].searchParams.get("limit"), "1");
  });
});

describe("car", () => {
  for (const listing of ["42793038", 42793038, "encar:42793038"]) {
    it(`accepts ${JSON.stringify(listing)}`, async () => {
      const { api, urls } = setup(car("encar:42793038"));
      assert.equal((await api.car(listing)).id, "encar:42793038");
      assert.equal(urls[0].pathname, "/v1/cars/encar:42793038");
    });
  }

  for (const bad of ["", "  ", "other:1", "encar:"]) {
    it(`rejects ${JSON.stringify(bad)}`, () => {
      assert.throws(() => carId(bad), TypeError);
    });
  }

  it("throws the apiauto errors", async () => {
    const { api } = setup({ __status: 404, body: { error: { code: "not_found", message: "no such car" } } });
    await assert.rejects(api.car("1"), NotFoundError);
  });
});

describe("changes", () => {
  it("presets the market", async () => {
    const feed = {
      items: [
        { id: 1, car_id: "encar:1", type: "added" },
      ],
      next_cursor: null,
    };
    const { api, urls } = setup(feed, feed);
    const result = await api.changes({ since: "2026-11-01T00:00:00Z", type: ["added", "price_drop"] });
    assert.deepEqual(
      result.items.map((c) => c.car_id),
      ["encar:1"],
    );
    assert.equal(urls[0].searchParams.get("market"), "kr");
    assert.deepEqual(urls[0].searchParams.getAll("type"), ["added", "price_drop"]);
    const ids = [];
    for await (const c of api.iterChanges({ since: "2026-11-01T00:00:00Z", maxItems: 5 })) ids.push(c.id);
    assert.deepEqual(ids, [1]);
  });
});

describe("references", () => {
  it("brands, models and status use the market", async () => {
    const markets = {
      items: [
        { market: "kr", source: "encar" },
        { market: "cn", source: "che168" },
        { market: "us", source: "copart+iaai" },
      ],
    };
    const { api, urls } = setup([{ name: "Hyundai", count: 5 }], [{ name: "Grandeur", count: 2 }], markets);
    assert.equal((await api.brands())[0].name, "Hyundai");
    assert.deepEqual(params(urls[0]), { market: "kr" });
    assert.equal((await api.models("Hyundai"))[0].count, 2);
    assert.deepEqual(params(urls[1]), { market: "kr", brand: "Hyundai" });
    assert.equal((await api.status()).market, "kr");
  });
});

describe("raw", () => {
  it("returns the raw fields or an empty object", () => {
    assert.deepEqual(raw({ raw: { source_values: { brand: "x" } } }).source_values, { brand: "x" });
    assert.deepEqual(raw({}), {});
  });
});
