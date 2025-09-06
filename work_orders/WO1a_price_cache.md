# Work Order 1a — Addendum: Price Cache

PERSONA: Data Engineer (primary)

CONTEXT:
This extends **WO1_data_and_signals.md**. Implement a CSV-based cache to minimize redundant network calls while ensuring daily freshness.

OBJECTIVES:
1) Add on-disk caching for yfinance price data.
2) Ensure freshness (≤ 1 trading day old) before using cache.
3) Provide clear logs for cache hit/refresh/error.

DELIVERABLES (update only these paths):
- `src/growthbrief/data.py` — augment `get_prices()` with caching:
  - Cache path: `data/cache/{SYMBOL}.csv` (Adj Close only, date-indexed).
  - Freshness: last row date ≥ latest market close; else refresh from yfinance and overwrite.
  - Corruption handling: if parse error/empty → delete and re-fetch.
  - Logging:
    - `[green]CACHE HIT[/green] {symbol}`
    - `[yellow]REFRESH[/yellow] {symbol}`
    - `[red]CACHE ERROR[/red] {symbol} → re-fetching`
- `tests/growthbrief/test_data.py` — add tests for cache-hit, cache-stale, and cache-corrupt scenarios (use temp dir or monkeypatch paths).
- (Optional) `data/cache/README.md` — note that cached CSVs are ephemeral.

ACCEPTANCE CRITERIA:
- Running `python scripts/run_signals.py` twice on the same day shows CACHE HIT on the second run.
- Corrupted/missing/old cache triggers refresh without crashing.
- All tests pass via `make test`.
