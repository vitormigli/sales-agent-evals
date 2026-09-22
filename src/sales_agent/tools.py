"""Tool definitions (OpenAI function-calling schema) and implementations.
Customer-facing tools write to the CRM; internal tools only read from it."""

import json

from sales_agent.catalog import find_products, get_product
from sales_agent.crm import CRM

CUSTOMER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_produto",
            "description": "Busca produtos no catálogo por nome ou categoria.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_estoque",
            "description": "Consulta a quantidade em estoque de um produto pelo ID.",
            "parameters": {
                "type": "object",
                "properties": {"product_id": {"type": "string"}},
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_lead",
            "description": "Registra um novo lead interessado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "contato": {"type": "string"},
                    "interesse": {"type": "string"},
                },
                "required": ["nome", "contato"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "agendar_retorno",
            "description": "Agenda um retorno/contato futuro com um lead já registrado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "integer"},
                    "data": {"type": "string", "description": "formato dd/mm/aaaa"},
                    "hora": {"type": "string", "description": "formato HH:MM"},
                },
                "required": ["lead_id", "data", "hora"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalar_para_humano",
            "description": (
                "Encaminha a conversa para um atendente humano quando o pedido está fora "
                "do escopo do agente ou o cliente pede explicitamente para falar com alguém."
            ),
            "parameters": {
                "type": "object",
                "properties": {"motivo": {"type": "string"}},
                "required": ["motivo"],
            },
        },
    },
]

INTERNAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_metricas",
            "description": (
                "Retorna métricas agregadas do CRM: total de leads, por status, agendamentos."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_leads",
            "description": "Lista leads, opcionalmente filtrando por status.",
            "parameters": {
                "type": "object",
                "properties": {"status": {"type": "string"}},
            },
        },
    },
]


def execute_customer_tool(name: str, arguments: dict, crm: CRM) -> dict:
    if name == "buscar_produto":
        results = find_products(arguments["query"])
        produtos = [{"id": p["id"], "nome": p["nome"], "preco": p["preco"]} for p in results]
        return {"produtos": produtos}

    if name == "consultar_estoque":
        product = get_product(arguments["product_id"])
        if not product:
            return {"error": "produto não encontrado"}
        return {"product_id": product["id"], "estoque": product["estoque"]}

    if name == "registrar_lead":
        lead_id = crm.register_lead(
            arguments["nome"], arguments["contato"], arguments.get("interesse")
        )
        return {"lead_id": lead_id, "status": "registrado"}

    if name == "agendar_retorno":
        appointment_id = crm.schedule_followup(
            arguments["lead_id"], arguments["data"], arguments["hora"]
        )
        return {"appointment_id": appointment_id, "status": "agendado"}

    if name == "escalar_para_humano":
        return {"status": "encaminhado", "motivo": arguments.get("motivo", "")}

    return {"error": f"unknown tool {name}"}


def execute_internal_tool(name: str, arguments: dict, crm: CRM) -> dict:
    if name == "consultar_metricas":
        return crm.metrics()
    if name == "listar_leads":
        return {"leads": crm.list_leads(arguments.get("status"))}
    return {"error": f"unknown tool {name}"}


def tool_result_message(tool_call_id: str, result: dict) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": json.dumps(result, ensure_ascii=False),
    }
