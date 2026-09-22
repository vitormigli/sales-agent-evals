"""Drives a simulated-customer LLM against the real customer agent for up to
MAX_TURNS exchanges, collecting the full transcript and tool-call log."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from openai import OpenAI

from sales_agent.agent import run_customer_agent
from sales_agent.crm import CRM

SIMULATOR_MODEL = "gpt-4o-mini"
MAX_TURNS = 4
STOP_TOKEN = "ENCERRAR"


def _customer_turn(client: OpenAI, persona: str, conversation_so_far: list[dict]) -> str:
    system = (
        f"{persona}\n\nVocê está simulando um cliente conversando com um assistente de "
        f"vendas por chat. Escreva só a fala do cliente, uma mensagem por vez, em "
        f"português. Quando o objetivo estiver cumprido, inclua a palavra {STOP_TOKEN} "
        "na sua mensagem."
    )
    messages = [{"role": "system", "content": system}]
    for turn in conversation_so_far:
        role = "assistant" if turn["role"] == "customer" else "user"
        messages.append({"role": role, "content": turn["content"]})
    if not conversation_so_far:
        messages.append({
            "role": "user",
            "content": (
                "Escreva agora a primeira mensagem do cliente, indo direto ao ponto "
                "descrito no seu objetivo acima — não faça uma pergunta genérica."
            ),
        })

    response = client.chat.completions.create(model=SIMULATOR_MODEL, messages=messages)
    return response.choices[0].message.content or ""


def run_scenario(client: OpenAI, scenario: dict, db_path: Path) -> dict:
    crm = CRM(db_path)
    transcript: list[dict] = []
    all_tool_calls: list[dict] = []
    history: list[dict] = []

    conversation_for_customer: list[dict] = []

    for _turn in range(MAX_TURNS):
        customer_msg = _customer_turn(client, scenario["persona"], conversation_for_customer)
        conversation_for_customer.append({"role": "customer", "content": customer_msg})
        transcript.append({"role": "user", "content": customer_msg})

        stop = STOP_TOKEN in customer_msg
        clean_msg = customer_msg.replace(STOP_TOKEN, "").strip()

        run = run_customer_agent(client, crm, history, clean_msg or customer_msg)
        history = run.messages[1:]  # drop system prompt for next-turn history
        all_tool_calls.extend(run.tool_calls_log)
        transcript.append({"role": "assistant", "content": run.final_text})
        conversation_for_customer.append({"role": "agent", "content": run.final_text})

        if stop:
            break

    return {
        "id": scenario["id"],
        "transcript": transcript,
        "tool_calls_log": all_tool_calls,
        "n_turns": len(transcript) // 2,
        "success": scenario["success_check"](all_tool_calls, transcript),
    }
