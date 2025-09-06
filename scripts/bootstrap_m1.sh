#!/usr/bin/env bash
set -euo pipefail

# --- Config -------------------------------------------------------------
# Usage: REPO="JeffESchmitz/growthbrief" ./scripts/bootstrap_m1.sh
: "${REPO:?Set REPO='owner/repo' before running, e.g. REPO='JeffESchmitz/growthbrief'}"

M1_TITLE='M1 — Core data & signals'
M2_TITLE='M2 — News + social + backtest'
M3_TITLE='M3 — Risk + paper trading'

# --- Helpers ------------------------------------------------------------
say() { printf "\n\033[1;34m==>\033[0m %s\n" "$*"; }
ok()  { printf "\033[0;32m✔\033[0m %s\n" "$*"; }
warn(){ printf "\033[0;33m⚠\033[0m %s\n" "$*"; }

create_label() {
  local name="$1" color="$2" desc="$3"
  if gh label list -R "$REPO" --search "$name" --limit 1 --json name --jq '.[0].name' | grep -q "^$name$"; then
    warn "Label exists: $name"
  else
    gh label create "$name" --color "$color" --description "$desc" -R "$REPO" >/dev/null && ok "Label created: $name"
  fi
}

ensure_milestone() {
  local title="$1" desc="${2:-}"
  local num
  num="$(gh api repos/"$REPO"/milestones --jq ".[] | select(.title==\"$title\") | .number" | head -n1 || true)"
  if [[ -z "${num}" ]]; then
    gh api -X POST repos/"$REPO"/milestones -f title="$title" -f description="$desc" >/dev/null
    ok "Milestone created: $title"
    num="$(gh api repos/"$REPO"/milestones --jq ".[] | select(.title==\"$title\") | .number")"
  else
    warn "Milestone exists: $title"
  fi
  echo "$num"
}

issue_create() {
  local title="$1" body="$2" milestone="$3"; shift 3
  local labels=("$@") label_flags=()
  for L in "${labels[@]}"; do label_flags+=(-l "$L"); done

  # Create issue (stdout prints URL); then query its number
  local url
  url="$(gh issue create -R "$REPO" -t "$title" -b "$body" -m "$milestone" "${label_flags[@]}" | tail -n1)"
  local num
  num="$(gh issue list -R "$REPO" --state open --search "in:title \"$title\"" --json number,url --jq '.[0].number')"
  echo "$num $url"
}

# --- Checks -------------------------------------------------------------
say "Checking repo access: $REPO"
gh repo view "$REPO" >/dev/null && ok "Repo reachable"

# --- Milestones ---------------------------------------------------------
say "Ensuring milestones"
M1_NUM="$(ensure_milestone "$M1_TITLE" 'WO1 + WO1a')"
M2_NUM="$(ensure_milestone "$M2_TITLE" 'News ingest, social, backtest')"
M3_NUM="$(ensure_milestone "$M3_TITLE" 'Risk engine + paper trading')"

# --- Labels -------------------------------------------------------------
say "Ensuring labels"

# Type
create_label 'type: feat'  '1f883d' 'New feature'
create_label 'type: fix'   'd73a4a' 'Bug fix'
create_label 'type: chore' '6a737d' 'Infra/cleanup'
create_label 'type: docs'  '0e8a16' 'Docs'
create_label 'type: test'  'fbca04' 'Testing'

# Area
for L in 'area:data' 'area:signals' 'area:news' 'area:social' 'area:llm' 'area:backtest' 'area:risk' 'area:reports' 'area:infra'; do
  create_label "$L" '0052cc' 'Area'
done

# Persona
for P in 'persona:router-pm' 'persona:data-engineer' 'persona:signals-policy' 'persona:news-ingestor' 'persona:social-analyst' 'persona:llm-analyst' 'persona:backtester' 'persona:risk-officer' 'persona:reporter' 'persona:paper-trader'; do
  create_label "$P" 'a371f7' 'Persona'
done

# Priority
create_label 'P1' 'b60205' 'High priority'
create_label 'P2' 'd93f0b' 'Medium priority'
create_label 'P3' 'fbca04' 'Low priority'

# --- Issues (M1) --------------------------------------------------------
say "Creating M1 issues"

declare -a CREATED

read -r n url < <(issue_create \
  "Repo hygiene: verify structure & Makefile" \
  "Confirm tree matches intended layout; ensure Makefile install/test/cov works; remove stray artifacts; Python 3.11 compatibility." \
  "$M1_TITLE" \
  "type: chore" "area:infra" "persona:router-pm")
CREATED+=("#$n $url")

read -r n url < <(issue_create \
  "WO1: Implement data.get_prices() with yfinance" \
  "Historical Adj Close for tickers.csv with retries/backoff; warn+skip short history; optional cache path decided in WO1a." \
  "$M1_TITLE" \
  "type: feat" "area:data" "persona:data-engineer")
CREATED+=("#$n $url")

read -r n url < <(issue_create \
  "WO1: Implement signals.compute() core metrics" \
  "SMA50/100/200, six_month_momentum_pct, 20d volatility, is_uptrend (price > 100DMA). Deterministic." \
  "$M1_TITLE" \
  "type: feat" "area:signals" "persona:signals-policy")
CREATED+=("#$n $url")

read -r n url < <(issue_create \
  "WO1: CLI runner to print & save signals" \
  "scripts/run_signals.py reads tickers.csv → prints table → saves data/signals_{date}.csv." \
  "$M1_TITLE" \
  "type: feat" "area:infra" "persona:data-engineer")
CREATED+=("#$n $url")

read -r n url < <(issue_create \
  "WO1: Unit tests for data & signals" \
  "pytest + vcrpy/responses; fixtures; ensure determinism; cover edge cases." \
  "$M1_TITLE" \
  "type: test" "area:data" "area:signals" "persona:data-engineer" "persona:signals-policy")
CREATED+=("#$n $url")

read -r n url < <(issue_create \
  "WO1a: CSV cache with freshness ≤ 1 day" \
  "data/cache/{SYMBOL}.csv; CACHE HIT/REFRESH/ERROR logs; corrupt → re-fetch; tests for hit/refresh/corrupt." \
  "$M1_TITLE" \
  "type: feat" "area:data" "persona:data-engineer")
CREATED+=("#$n $url")

read -r n url < <(issue_create \
  "Docs: README Quick Start for M1.1" \
  "Add commands to install, run signals, explain cache." \
  "$M1_TITLE" \
  "type: docs" "area:infra" "persona:reporter")
CREATED+=("#$n $url")

say "Created issues (number and URL):"
for line in "${CREATED[@]}"; do echo "  $line"; done

say "Done."
