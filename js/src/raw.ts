// Types of the Encar-only fields of a record (`car.raw`).
/** The ECB daily rate behind `price_usd`. */
export interface FxQuote {
  currency: string;
  /** Decimal string: US dollars for one unit of `currency`. */
  usd_per_unit: string;
  date: string;
  source: string;
}

/** Encar-only fields of a record (`car.raw`). Every key is optional. */
export interface EncarRaw {
  /** Encar's badge (trim) in Korean, as the listing shows it. */
  badge?: string | null;
  badge_detail?: string | null;
  /** The dealer's province in Korean, for example `경기`. */
  office_city?: string | null;
  /** `normal`, `lease` or `rental`: lease and rental listings show a monthly payment, not a price. */
  sell_type?: string | null;
  has_vin?: boolean;
  /** The model-year code, `YYYYMM`. */
  form_year?: string | null;
  body_class?: string | null;
  condition?: string[];
  trust?: string[];
  service_mark?: string[];
  /** Encar's own Korean spellings of make, model, trim, fuel and region. */
  source_values?: Record<string, string | null>;
  fx?: FxQuote | null;
}
