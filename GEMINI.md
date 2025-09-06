# Gemini Notes

This is a personal file for tracking Gemini interactions and notes about this repository.

---

# Project Overview

## `growthbrief`

*   **Project:** `growthbrief` is an experimental Python-based toolkit for portfolio and AI analysis.
*   **Technologies:** It uses Python 3.11 with libraries like `pandas`, `pydantic`, `vectorbt`, `yfinance`, and `alpaca-trade-api`.
*   **Structure:** The project is organized into `src` for the main code, `prompts` for persona and LLM instructions, and `schema` for data definitions. The source code is stubbed out, ready for implementation.
*   **Configuration:** API keys and other secrets are managed via a `.env` file.

---

# Development Plan

## Milestones

**M0. Scaffolding (already provided)**
* Repo + personas + schema + stubs.

**M1. Core market data → signals → brief (no social yet)**
1. **Data Engineer** — price ingestion (`data.py`) with retries/caching.  
2. **Signals & Policy** — SMA/momentum/volatility + `is_uptrend` (`signals.py`).  
3. **News Ingestor** — 5–10 headlines/ticker normalized (`news.py`).  
4. **LLM Analyst** — produce strict JSON per `schema/analysis.schema.json` (`llm.py`).  
5. **Reporter** — render the Daily Brief (Markdown/HTML) (`brief.py`).  

**M2. Social + backtest**  
6. **Social Analyst** — Reddit mentions/claims snapshot (`social.py`).  
7. **Backtester** — vectorized backtest of policy (`backtest.py`).  

**M3. Risk & paper trading (optional)**  
8. **Risk Officer** — rules validation (`risk.py`).  
9. **Paper Trader** — Alpaca paper toggle (`scripts/paper_trade.py`).  

---

# Testing Strategy

* **Framework:** `pytest`  
* **Location:** root-level `tests/` mirroring `src/growthbrief/`  
* **Naming:** `tests/growthbrief/test_<module>.py`  
* **Coverage:** use `pytest-cov`; target ≥ 70% in M1, higher later  
* **HTTP:** record/memoize network calls with `vcrpy` **or** stub via `responses`  
* **Randomness:** deterministic seeds; no time-based flakiness  
* **Fixtures:** lightweight fixtures in `tests/conftest.py` (sample price DF, sample headlines JSON)  

---

# Persona Kit (for Gemini CLI)

Personas are **specialists**. Each task must name exactly one persona. No persona should attempt repo-wide refactors, sweeping chores, or multi-milestone jumps.

---

### 0) **Router / Project Manager**
* Dispatches tasks to the right persona.
* Never implements code.
* Outputs JSON with `{persona, objectives, checklist, clarify}`.

### 1) **Data Engineer**
* Ingests prices/fundamentals, handles retries, caching.
* Guarantees: typed, idempotent, `.env` for keys.

### 2) **News Ingestor**
* Fetches N headlines per ticker, normalizes to `{title, source, published, url}`.
* Dedupes, UTC timestamps, caches JSON.

### 3) **Social Analyst**
* Scans Reddit (later X/Twitter).
* Counts mentions, extracts top claims, no NLP yet.

### 4) **Signals & Policy**
* Computes SMA/momentum/volatility.
* Applies entry/exit rules from risk policy.

### 5) **LLM Analyst**
* Summarizes inputs and emits JSON (strict schema).
* Uses retry + validation.

### 6) **Backtester**
* Runs vectorized backtests with signals + simulated news.
* Outputs metrics and charts.

### 7) **Paper Trader (Alpaca)**
* Converts actions → target weights.
* Posts paper trades (dry-run unless confirmed).

### 8) **Reporter**
* Renders Daily Brief in Markdown + HTML.
* Embeds tables, charts, logs.

### 9) **Risk Officer**
* Enforces the risk policy.
* Flags concentration, drawdown, stop/target breaches.

### 10) **Governor**
* Scope limiter.
* If a task is oversized, outputs TODOs + trimmed scope.

---

# Lane Discipline (Must Stay in Lane)

Gemini must **NOT**:
- Work on more than one GitHub issue at a time.
- Touch files outside the listed deliverables.
- Modify build/CI/CD configs, LICENSE, README, or repo metadata unless explicitly instructed.
- Perform “chore” sweeping changes (e.g., rename all, reformat all).
- Delete more than a handful of lines without explicit approval.
- Create new personas or alter the persona kit.
- Push directly to `main` or merge branches without human approval.

---

# Workflow Contract

Every Gemini task must follow this sequence:

1. **PLAN**  
   - Generate `PLAN.md` with objectives, steps, and list of target files.  
   - Output only the plan, no code yet.  

2. **APPROVAL**  
   - Wait for human review of the plan.  
   - If not approved, stop.  

3. **PATCH**  
   - Produce a unified diff (`.patch`) scoped to the files in the plan.  
   - Never exceed MAX 50 changed files or MAX 200 deletions.  
   - Apply repo `.gemini-allowlist` and `.gemini-blocklist`.  

4. **REVIEW**  
   - Show patch stats and preview.  
   - Human must approve before applying.  

5. **DRAFT PR**  
   - Commit with `feat: <issue title> (Refs #<issue>)`.  
   - Open as **Draft PR** labeled `ai-generated` and `needs-review`.  

---

# Safety Checklist

Before producing a patch, Gemini must confirm:

- [ ] Task is scoped to **one GitHub issue**.  
- [ ] Persona is correctly assigned and narrow.  
- [ ] Output files match the deliverables list only.  
- [ ] No modifications to blocked files (`.github/`, `.gitignore`, `.env`, configs).  
- [ ] Changes are idempotent and deterministic.  
- [ ] Unit tests or stubs are added where applicable.  
- [ ] Secrets never hardcoded.  
- [ ] Rate limits respected.  
- [ ] If ambiguous → emit `TODO:` and stop.  

---

# Standard Task Header

```
PERSONA: <choose one from Persona Kit>

CONTEXT:
- Repo: growthbrief
- Environment: Python 3.11; macOS
- Secrets: .env (never hardcode)
- Style: typed, documented, small pure functions
- Non-goals: live trading, personal advice, full UI

DELIVERABLES:
- Only the files listed below. No extra commentary except final "CHANGES:" list.

QUALITY BARS:
- Determinism, idempotence, clear errors, small PRs
- Unit tests where applicable

GUARDRAILS:
- No credentials in code
- Respect API rate limits and TOS
- Stay within persona scope
- Do not exceed allowlist/blocklist
- If unknown/ambiguous, emit TODOs and stop
```

---

# Example Work Order

```
PERSONA: LLM Analyst
TASK: Implement `llm.analyze_tickers()` to emit JSON conforming to schema/analysis.schema.json
INPUTS: data/signals_*.csv, data/news/*.json, data/social/*.json
OUTPUT FILES:
- src/growthbrief/llm.py
- prompts/SYSTEM_PROMPT.md
- prompts/USER_PROMPT.md
- reports/analysis_{date}.json (example)
ACCEPTANCE:
- Invalid JSON retried up to 2x
- Pydantic validates; file saved
CHANGES: (list files)
```
