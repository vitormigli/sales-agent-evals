"""Runs all simulated-customer scenarios, scores them, and writes
evals/results.json, evals/results.md, and per-scenario transcripts."""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from scenarios import SCENARIOS  # noqa: E402
from simulate import run_scenario  # noqa: E402

from sales_agent.guardrails import has_price_hallucination  # noqa: E402

EVALS_DIR = Path(__file__).parent
TRANSCRIPTS_DIR = EVALS_DIR / "transcripts"


def score_guardrails(result: dict) -> int:
    violations = 0
    for msg in result["transcript"]:
        if msg["role"] == "assistant":
            if has_price_hallucination(msg["content"], result["tool_calls_log"]):
                violations += 1
    return violations


def main() -> None:
    client = OpenAI()
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for scenario in SCENARIOS:
        print(f"=== {scenario['id']} ===")
        db_path = EVALS_DIR.parent / "data" / f"eval_{scenario['id']}.db"
        result = run_scenario(client, scenario, db_path)
        result["guardrail_violations"] = score_guardrails(result)
        results.append(result)

        (TRANSCRIPTS_DIR / f"{scenario['id']}.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"  success={result['success']} turns={result['n_turns']} "
              f"violations={result['guardrail_violations']}")

    task_completion_rate = sum(r["success"] for r in results) / len(results)
    total_violations = sum(r["guardrail_violations"] for r in results)
    avg_turns = statistics.mean(r["n_turns"] for r in results)

    summary = {
        "n_scenarios": len(results),
        "task_completion_rate": task_completion_rate,
        "total_guardrail_violations": total_violations,
        "avg_turns_to_completion": avg_turns,
        "scenarios": [
            {
                "id": r["id"],
                "success": r["success"],
                "n_turns": r["n_turns"],
                "guardrail_violations": r["guardrail_violations"],
            }
            for r in results
        ],
    }

    (EVALS_DIR / "results.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = ["# Agent Evaluation Results", ""]
    lines.append(f"{len(results)} simulated conversations, capped at 4 turns each.\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Task completion rate | {task_completion_rate:.1%} |")
    lines.append(f"| Guardrail violations (total) | {total_violations} |")
    lines.append(f"| Avg. turns to completion | {avg_turns:.1f} |")
    lines.append("")
    lines.append("## Per-scenario results")
    lines.append("")
    lines.append("| Scenario | Success | Turns | Guardrail violations |")
    lines.append("|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['id']} | {'✅' if r['success'] else '❌'} | {r['n_turns']} | "
            f"{r['guardrail_violations']} |"
        )
    (EVALS_DIR / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
