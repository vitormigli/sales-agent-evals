# 1. SQLite instead of Postgres for the fictional CRM

## Status

Accepted (deviates from the master plan, which suggested Postgres)

## Context

The CRM here is fictional and small (leads, appointments, per-session messages).
Postgres would need its own container, a wait-for-healthy step, and connection
config — real cost in `docker compose up` startup time and moving parts for no
functional benefit at this scale.

## Decision

Use SQLite via the standard library (`sqlite3`), one file under `data/crm.db`.

## Consequences

- `docker compose up` starts one container instead of two.
- No concurrent-write concerns worth worrying about at this scale.
- If this agent design were reused against a real, larger CRM, swapping the `CRM`
  class's SQL for Postgres is a contained change — every caller only sees its
  Python methods (`register_lead`, `schedule_followup`, `metrics`, ...).
