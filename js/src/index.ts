/**
 * encar-api — Encar API client for JavaScript and TypeScript: South Korean used-car listings from Encar as JSON.
 *
 * A thin layer over the apiauto.space client (`apiauto`) with the market preset to `kr`.
 * From the apiauto.space team. Not affiliated with Encar or SK Encar.
 *
 * @see https://apiauto.space/en/encar-api/
 * @packageDocumentation
 */
import { Apiauto } from "apiauto";
import type {
  ApiautoOptions,
  Car,
  CarsPage,
  CarsParams,
  Change,
  ChangesPage,
  ChangesParams,
  Dictionaries,
  IterOptions,
  MarketStatus,
  ReferenceItem,
  Usage,
} from "apiauto";
import type { EncarRaw } from "./raw.js";

export {
  APIConnectionError,
  Apiauto,
  ApiautoError,
  AuthenticationError,
  BadRequestError,
  NotFoundError,
  PermissionDeniedError,
  QuotaExceededError,
  RateLimitError,
  ServerError,
  ServiceUnavailableError,
} from "apiauto";
export type {
  ApiautoOptions,
  Car,
  CarsPage,
  Change,
  ChangesPage,
  ChangeType,
  Decimal,
  Dictionaries,
  Location,
  MarketStatus,
  Price,
  ReferenceItem,
  ResponseInfo,
  Usage,
} from "apiauto";
export type { EncarRaw, FxQuote } from "./raw.js";
export { VERSION } from "./version.js";

/** The apiauto.space market of Encar. */
export const MARKET = "kr" as const;
/** The `source` of every record this package returns. */
export const SOURCE = "encar" as const;
/** `true` when the market also holds another source and records are filtered on the client. */
export const SHARED_MARKET: boolean = false;

/** Filters of {@link EncarApi.cars}: those of `GET /v1/cars` without `market`. */
export type CarsFilters = Omit<CarsParams, "market">;
/** Parameters of {@link EncarApi.changes}: those of `GET /v1/changes` without `market`. */
export type ChangesFilters = Omit<ChangesParams, "market">;

/**
 * The full record id for a Encar listing number: `42793038` → `encar:42793038`.
 * An id with the `encar:` prefix is returned as is; another source's prefix throws.
 */
export function carId(listing: string | number): string {
  const text = String(listing).trim();
  if (text === "") throw new TypeError("encar-api: listing must not be empty");
  const sep = text.indexOf(":");
  if (sep === -1) return `${SOURCE}:${text}`;
  if (text.slice(0, sep) !== SOURCE || sep === text.length - 1) {
    throw new TypeError(`encar-api: not a Encar id: ${JSON.stringify(text)}`);
  }
  return text;
}

/** The Encar-only fields of a record (`car.raw`), typed. */
export function raw(car: Car): EncarRaw {
  return (car.raw ?? {}) as EncarRaw;
}


/**
 * Encar client of the apiauto.space API. Server-side only: the API does not accept
 * browser requests, and a key in page code is visible to every visitor.
 *
 * @example
 * ```ts
 * import { EncarApi } from "encar-api";
 *
 * const api = new EncarApi(); // reads APIAUTO_KEY
 * const page = await api.cars({ brand: "Hyundai", year_min: 2020, limit: 20 });
 * for (const car of page.items) console.log(car.id, car.title, car.price.amount);
 * ```
 */
export class EncarApi {
  /** The general client, for anything this one does not wrap. */
  readonly core: Apiauto;

  /** @param options - The key defaults to the `APIAUTO_KEY` environment variable. */
  constructor(options: ApiautoOptions = {}) {
    this.core = new Apiauto(options);
  }

  /** One page of Encar cars. Prices are in KRW; every car returned counts against the quota. */
  async cars(filters: CarsFilters = {}): Promise<CarsPage> {
    const page = await this.core.cars({ ...filters, market: MARKET });
    return page;
  }

  /** Every Encar car matching the filters, page after page; `maxItems` stops early. */
  async *iterCars(filters: CarsFilters & IterOptions = {}): AsyncGenerator<Car, void, undefined> {
    yield* this.core.iterCars({ ...filters, market: MARKET });
  }

  /**
   * One car by listing number (`42793038`) or record id (`encar:42793038`).
   * Cars taken off sale stay available for 14 days with `is_active: false`.
   */
  car(listing: string | number): Promise<Car> {
    return this.core.car(carId(listing));
  }

  /** One page of the change feed: new cars, cars taken off sale and price changes since a moment. */
  async changes(params: ChangesFilters): Promise<ChangesPage> {
    const page = await this.core.changes({ ...params, market: MARKET });
    return page;
  }

  /** Every event of the change feed since a moment, page after page. */
  async *iterChanges(params: ChangesFilters & IterOptions): AsyncGenerator<Change, void, undefined> {
    yield* this.core.iterChanges({ ...params, market: MARKET });
  }

  /** Makes of the kr market with car counts, most frequent first. Free. */
  brands(): Promise<ReferenceItem[]> {
    return this.core.brands(MARKET);
  }

  /** Models of a make with car counts. Free. */
  models(brand: string): Promise<ReferenceItem[]> {
    return this.core.models(MARKET, brand);
  }

  /** Canonical values of `fuel`, `transmission`, `body_type` and more. Free. */
  dictionaries(): Promise<Dictionaries> {
    return this.core.dictionaries();
  }

  /** The kr market: plan access, data age and the number of active cars. Free. */
  async status(): Promise<MarketStatus> {
    const market = (await this.core.markets()).find((item) => item.market === MARKET);
    if (market === undefined) throw new Error(`encar-api: the API did not list the ${MARKET} market`);
    return market;
  }

  /** The plan, its term and how much of the quota is spent. Free. */
  usage(): Promise<Usage> {
    return this.core.usage();
  }
}
