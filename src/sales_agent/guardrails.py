"""Lightweight, testable heuristics for guardrail-violation detection: did the
agent state a price or stock number that wasn't actually returned by a tool call?"""

import re

PRICE_PATTERN = re.compile(r"R\$\s*[\d.,]+")


def _numbers_in_text(text: str) -> set[str]:
    return {re.sub(r"[^\d]", "", m) for m in PRICE_PATTERN.findall(text)}


def _numbers_in_tool_results(tool_calls_log: list[dict]) -> set[str]:
    numbers = set()
    for call in tool_calls_log:
        result = call.get("result", {})
        for value in _flatten_values(result):
            if isinstance(value, (int, float)):
                numbers.add(re.sub(r"[^\d]", "", f"{value:.2f}"))
                numbers.add(str(int(value)))
    return numbers


def _flatten_values(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _flatten_values(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _flatten_values(v)
    else:
        yield obj


def has_price_hallucination(assistant_text: str, tool_calls_log: list[dict]) -> bool:
    """Returns True if the assistant's message states a price (R$ ...) that
    doesn't match any number returned by a tool call in this conversation."""
    stated = _numbers_in_text(assistant_text)
    if not stated:
        return False
    grounded = _numbers_in_tool_results(tool_calls_log)
    return not stated.issubset(grounded)
