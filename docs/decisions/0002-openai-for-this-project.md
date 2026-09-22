# 2. OpenAI instead of Claude for this project

## Status

Accepted

## Context

Every other project in this portfolio uses the Claude API directly (per the master
plan's stack). This project was built when the Anthropic API budget for the
portfolio work was nearly exhausted, and an OpenAI key was available instead.

## Decision

Use the OpenAI SDK (`openai`) and `gpt-4o-mini` for both agents' chat-completions +
tool-calling loop, rather than switching the whole portfolio's convention.

## Consequences

- This is the one repo in the portfolio that isn't built on the Claude API — worth
  being upfront about in interviews rather than glossing over.
- The agent loop (`src/sales_agent/agent.py`) only touches the OpenAI client in one
  place (`_run`'s `client.chat.completions.create` call and the tool-call shape it
  parses) — porting it to `anthropic`'s Messages API + tool use is a contained,
  mechanical change, not a redesign, if this needs to move back to Claude later.
