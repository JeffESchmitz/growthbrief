#!/usr/bin/env bash
# GrowthBrief Doctor — quick sanity, tests, and run
set -euo pipefail

say() { printf "\033[1m%s\033[0m\n" "$*"; }
ok()  { printf "✅ %s\n" "$*"; }
warn(){ printf "⚠️  %s\n" "$*"; }
die() { printf "❌ %s\n" "$*" ; exit 1; }

# 0) Repo checks
git rev-parse --show-toplevel >/dev/null 2>&1 || die "Run this from INSIDE the repo."
if [ -n "$(git status --porcelain)" ]; then
  warn "Working tree is not clean (that's ok for tests)."
fi

# 1) Python/venv
say "Setting up Python environment (3.11-compatible)…"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv || die "Could not create .venv"
fi
# shellcheck disable=SC1091
source .venv/bin/activate || die "Could not activate .venv"

python -V || true
python -m pip install --upgrade pip >/dev/null
python -m pip install -e .[dev] >/dev/null || warn "Editable install failed; continuing"

# 2) Lint & tests
say "Running lint & unit tests…"
python -m pip install ruff pytest pytest-cov >/dev/null
ruff check src tests || warn "Ruff found issues"
pytest -q --maxfail=1 --disable-warnings || die "Unit tests failed"
ok "Lint & tests OK"

# 3) Run signals/GRS
say "Running signals/GRS CLI…"
if [ -f "scripts/run_signals.py" ]; then
  python scripts/run_signals.py || die "signals script failed"
else
  warn "scripts/run_signals.py not found; skipping"
fi

# 4) Show latest artifacts
say "Looking for CSV artifacts…"
last_sig=$(ls -1t data/signals_*.csv 2>/dev/null | head -n1 || true)
last_grs=$(ls -1t data/grs_*.csv 2>/dev/null | head -n1 || true)

[ -n "$last_sig" ] && ok "Latest signals CSV: $last_sig" || warn "No signals CSV found"
[ -n "$last_grs" ] && ok "Latest GRS CSV: $last_grs" || warn "No GRS CSV found yet"

if [ -f "data/grs_latest.csv" ]; then
  say "Top 5 by GRS (from data/grs_latest.csv)…"
  python - <<'PY'
import pandas as pd
df = pd.read_csv('data/grs_latest.csv')
cols = [c for c in df.columns if c.lower() in ('symbol','ticker','grs','price','six_month_pct')]
if not cols:
    cols = df.columns.tolist()[:6]
print(df.sort_values('GRS', ascending=False)[cols].head(5).to_string(index=False))
PY
else
  warn "data/grs_latest.csv not present (expected after Step 5)."
fi

# 5) Backtest (optional)
if [ -f "scripts/run_backtest.py" ]; then
  say "Backtest available. Example run:"
  echo "  python scripts/run_backtest.py --tickers data/tickers.csv --topn 5 --start 2018-01-01 --end 2025-09-01"
else
  warn "scripts/run_backtest.py not present yet; skipping"
fi

ok "Done."
