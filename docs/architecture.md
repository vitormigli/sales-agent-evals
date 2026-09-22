# Architecture

```mermaid
flowchart TD
    U[User message] --> L[Agent loop: chat.completions + tools, tool_choice=auto]
    L -->|tool_use| T[Execute tool locally]
    T --> CRM[(SQLite CRM: leads, appointments, messages)]
    T --> L
    L -->|no more tool calls| R[Final text reply]
```

Both the customer and internal agents share the same loop
(`src/sales_agent/agent.py`) — only the system prompt and tool set differ. The loop
caps at `MAX_TOOL_TURNS` to avoid runaway tool-call chains.
