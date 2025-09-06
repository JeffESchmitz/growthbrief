# Work Order 1 — Data Foundation & First Signals (M1.1)

PERSONA: Data Engineer (primary) + Signals & Policy (supporting)

CONTEXT:
- Repo: growthbrief
- Goal: Stand up robust price ingestion and compute first-cut signals so we can render a minimal Daily Brief.
- Scope: Prices only (Adj Close). Fundamentals, social, and backtesting come later.
- Env: Python 3.11, macOS
- Secrets: Use `.env` via python-dotenv. No credentials in code.
- Non-goals: UI, live trading, financial advice.

OBJECTIVES:
1) Implement resilient historical price ingestion for a small universe (CSV `tickers.csv`), default lookback 400 trading days.
2) Compute core signals: sma_50, sma_100, sma_200, six_month_momentum_pct, volatility_20d, is_uptrend (price > 100DMA).
3) Provide a simple CLI runner that prints a neat table and saves `data/signals_{date}.csv`.
4) Add unit tests and basic docs. Ensure deterministic outputs from the signals layer.

ASSUMPTIONS:
- Use `yfinance` for price ingestion (free, acceptable for MVP). You may add lightweight caching to `/data/cache/` to reduce calls.
- Adj Close is sufficient for signals.
- If a ticker has < 200 rows, skip it with a clear WARNING.
- Market closed days must be handled gracefully.
- Timezone-naive daily index is fine (use UTC dates).

DELIVERABLES (files to create/modify only):
- `src/growthbrief/data.py` — implement `get_prices(symbols: list[str], lookback_days: int = 400) -> pandas.DataFrame` (Adj Close, columns = symbols)
- `src/growthbrief/signals.py` — implement `compute(adj_close_df: "pd.DataFrame") -> dict[str, dict]`
- `scripts/run_signals.py` — CLI runner (reads `tickers.csv`, writes `data/signals_{date}.csv`, prints table)
- `tests/growthbrief/test_data.py` — unit tests w/ error handling, small integration happy path using VCR/stub
- `tests/growthbrief/test_signals.py` — unit tests for SMA/momentum/volatility and `is_uptrend`
- `README.md` — add a short “M1.1 Quick Start” section with CLI instructions

QUALITY BARS:
- Typed functions, docstrings, clear errors
- Idempotent runs; informative logs (use `rich.print` or `logging`)
- Unit tests with `pytest`; avoid network flakiness via `vcrpy` or `responses`
- Graceful degradation: return only tickers with valid data; warn for skipped

IMPLEMENTATION NOTES:
- **data.get_prices**:
  - Input: list of symbols (upper-cased), `lookback_days` default = 400.
  - Output: `pd.DataFrame` indexed by date, columns = symbols, values = Adj Close (float).
  - Use retry/backoff (e.g., 3 attempts, small sleep). 
  - Optional: on-disk CSV cache per symbol (e.g., `data/cache/{{symbol}}.csv`) with a simple freshness check (<= 1 day old).
- **signals.compute**:
  - Inputs: the Adj Close DF.
  - For each symbol:
    - sma_50/100/200 (simple moving averages on Adj Close)
    - six_month_momentum_pct = (price_today / price_approximately_126_trading_days_ago - 1) * 100
    - volatility_20d = rolling std dev of daily returns (last 20 trading days)
    - is_uptrend = (price_today > sma_100_today)
  - Return: `dict[symbol] -> metrics dict`
- **scripts/run_signals.py**:
  - Read `tickers.csv` from repo root (one symbol per line or `Symbol` header acceptable).
  - Call `get_prices` → `compute` → print a neat table (Symbol, Price, Δ6m%, SMA50/100/200, Vol20d, Uptrend).
  - Save CSV `data/signals_{{today}}.csv` with columns matching the metrics.

ACCEPTANCE CRITERIA:
- `make install` then `make test` passes (include your tests).
- `python scripts/run_signals.py` with the default `tickers.csv` prints a table and writes `data/signals_{today}.csv`.
- Skips invalid/short-history tickers with clear WARNING and continues for the rest.
- `yfinance` calls are recorded/mocked in tests to avoid network flakiness.

CHECKLIST:
- [ ] Implement `get_prices` with retries and (optional) caching.
- [ ] Implement `compute` per spec.
- [ ] Add CLI runner and friendly console output.
- [ ] Add unit tests with fixtures/mocking.
- [ ] Update README Quick Start.
- [ ] Run `make test` and provide a short CHANGELOG in the PR description.

CHANGES:
- Only the files listed under DELIVERABLES.
