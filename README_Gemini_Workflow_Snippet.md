## Working with Gemini (Agent Guardrails)

We use a constrained flow to keep AI-assisted changes safe and reviewable:

1. **One issue at a time** — never batch issues.
2. **Plan → Approve → Patch → Review → Draft PR**:
   - Gemini proposes `PLAN.md` (no code).
   - Human approves.
   - Gemini produces a patch limited by allowlist/blocklist.
   - Human approves patch preview.
   - Draft PR opened with labels `ai-generated` and `needs-review`.
3. **Hard limits**: ≤50 files changed, ≤200 deletions.
4. **Protected areas**: `.github/**`, `README.md`, `LICENSE`, `.env*`, `data/**`, `reports/**`, and project metadata are off-limits unless explicitly requested.

The allow/block lists live at repo root:

- `.gemini-allowlist` — files/directories that Gemini may modify.
- `.gemini-blocklist` — files/directories Gemini must not touch.