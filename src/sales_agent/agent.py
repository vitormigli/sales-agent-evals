"""Agent loop: calls OpenAI chat completions with tools, executes tool calls
locally, loops until the model returns a plain text answer. Two agents share
this loop with different system prompts and tool sets."""

import json
import os

from openai import OpenAI

from sales_agent.crm import CRM
from sales_agent.tools import (
    CUSTOMER_TOOLS,
    INTERNAL_TOOLS,
    execute_customer_tool,
    execute_internal_tool,
    tool_result_message,
)

DEFAULT_MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini")
MAX_TOOL_TURNS = 6

CUSTOMER_SYSTEM_PROMPT = """Você é um assistente de vendas de uma loja de móveis e \
eletrônicos de escritório. Seja cordial e objetivo.

Regras obrigatórias:
- NUNCA informe preço ou estoque de um produto sem antes chamar a ferramenta \
correspondente (buscar_produto / consultar_estoque). Não invente números.
- Se o cliente pedir algo fora do catálogo da loja (ex: outro tipo de produto, \
suporte técnico de outro sistema, assuntos pessoais), chame escalar_para_humano.
- Se o cliente pedir explicitamente para falar com uma pessoa, chame \
escalar_para_humano.
- Para registrar interesse do cliente, use registrar_lead com os dados que ele \
fornecer. Só agende um retorno (agendar_retorno) depois de ter um lead_id.
- Responda sempre em português.
"""

INTERNAL_SYSTEM_PROMPT = """Você é um assistente interno de operações. Você tem \
acesso somente-leitura ao CRM da equipe de vendas para responder perguntas sobre \
métricas e leads. Não invente números — sempre use as ferramentas disponíveis. \
Responda sempre em português, de forma direta."""


class AgentRun:
    def __init__(self, messages: list[dict], tool_calls_log: list[dict]):
        self.messages = messages
        self.tool_calls_log = tool_calls_log

    @property
    def final_text(self) -> str:
        return self.messages[-1]["content"] or ""


def _run(
    client: OpenAI,
    system_prompt: str,
    tools: list[dict],
    execute_tool,
    crm: CRM,
    history: list[dict],
    user_message: str,
    model: str,
) -> AgentRun:
    messages = [{"role": "system", "content": system_prompt}, *history,
                {"role": "user", "content": user_message}]
    tool_calls_log: list[dict] = []

    for _ in range(MAX_TOOL_TURNS):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=tools, tool_choice="auto"
        )
        choice = response.choices[0].message
        messages.append(choice.model_dump(exclude_none=True))

        if not choice.tool_calls:
            return AgentRun(messages, tool_calls_log)

        for tool_call in choice.tool_calls:
            name = tool_call.function.name
            try:
                arguments = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}
            result = execute_tool(name, arguments, crm)
            tool_calls_log.append({"name": name, "arguments": arguments, "result": result})
            messages.append(tool_result_message(tool_call.id, result))

    return AgentRun(messages, tool_calls_log)


def run_customer_agent(
    client: OpenAI, crm: CRM, history: list[dict], user_message: str, model: str = DEFAULT_MODEL
) -> AgentRun:
    return _run(
        client, CUSTOMER_SYSTEM_PROMPT, CUSTOMER_TOOLS, execute_customer_tool,
        crm, history, user_message, model,
    )


def run_internal_agent(
    client: OpenAI, crm: CRM, history: list[dict], user_message: str, model: str = DEFAULT_MODEL
) -> AgentRun:
    return _run(
        client, INTERNAL_SYSTEM_PROMPT, INTERNAL_TOOLS, execute_internal_tool,
        crm, history, user_message, model,
    )
