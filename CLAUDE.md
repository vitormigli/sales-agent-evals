# Project instructions for Claude

This project follows the rules of the portfolio master plan, with one documented
exception (OpenAI instead of Claude — see `docs/decisions/0002-openai-for-this-project.md`):

1. No client code or data — fictional store, catalog, and CRM
   (see `src/sales_agent/catalog.py`, `src/sales_agent/crm.py`).
2. No committed secrets — use `.env` (gitignored) and keep `.env.example` up to
   date. `gitleaks` runs on pre-commit and in CI.
3. Every project reports numeric evaluation metrics — see `evals/results.md`.
4. Everything runs with a single command: `docker compose up` or `make run`.
5. README in English, with a short "Resumo em português" section at the end.
   Header banner + badges matching the other portfolio repos.
6. Small, descriptive commits using Conventional Commits.
7. Prefer simplicity — a hand-rolled tool-call loop (`src/sales_agent/agent.py`),
   no agent framework.

## Layout

- `src/sales_agent/catalog.py` — fictional product catalog.
- `src/sales_agent/crm.py` — SQLite-backed leads/appointments/message history.
- `src/sales_agent/tools.py` — tool schemas + implementations (customer vs. internal).
- `src/sales_agent/agent.py` — the tool-call loop, shared by both agents.
- `src/sales_agent/guardrails.py` — heuristic price-hallucination checker.
- `evals/run_eval.py` — simulated-customer conversations against the real agent;
  costs real API money — do not run this without the user's awareness of the cost.
