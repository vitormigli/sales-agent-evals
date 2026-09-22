"""Simulated-customer scenarios for the eval harness. Each scenario drives a
second LLM call playing a customer with a persona and objective; success is
checked programmatically against the resulting tool-call log, not by a judge."""


def _called(tool_calls_log: list[dict], name: str) -> bool:
    return any(c["name"] == name for c in tool_calls_log)


SCENARIOS = [
    {
        "id": "price_inquiry",
        "persona": (
            "Você é um cliente educado que quer saber o preço do 'Headset sem fio Orbit'. "
            "Pergunte o preço diretamente. Quando receber uma resposta com o preço (ou a "
            "informação de que ele será verificado), diga 'ENCERRAR' e agradeça."
        ),
        "success_check": lambda log, transcript: _called(log, "buscar_produto"),
    },
    {
        "id": "out_of_stock",
        "persona": (
            "Você quer comprar o 'Monitor 27 UltraWide Nimbus'. Pergunte se tem em estoque. "
            "Se disserem que está indisponível, diga 'ENCERRAR' e agradeça de qualquer forma."
        ),
        "success_check": lambda log, transcript: _called(log, "consultar_estoque"),
    },
    {
        "id": "lead_registration",
        "persona": (
            "Você se chama Marina Souza, seu contato é marina.souza@example.com, e você "
            "tem interesse na 'Cadeira ergonômica Aurora'. Diga que quer ser contatada "
            "sobre esse produto e forneça seu nome e e-mail quando pedirem. Depois que "
            "confirmarem o cadastro, diga 'ENCERRAR'."
        ),
        "success_check": lambda log, transcript: _called(log, "registrar_lead"),
    },
    {
        "id": "lead_and_schedule",
        "persona": (
            "Você se chama Pedro Alves, contato (11) 98888-7777, interessado na 'Mesa de "
            "escritório Lumen 120cm'. Peça para ser cadastrado como lead e depois peça "
            "para agendar um retorno para o dia 20/10/2026 às 14:00. Quando confirmarem "
            "o agendamento, diga 'ENCERRAR'."
        ),
        "success_check": lambda log, transcript: (
            _called(log, "registrar_lead") and _called(log, "agendar_retorno")
        ),
    },
    {
        "id": "out_of_catalog",
        "persona": (
            "Você pergunta se a loja vende geladeiras (a loja vende móveis e eletrônicos "
            "de escritório, não eletrodomésticos de cozinha). Depois da resposta, diga "
            "'ENCERRAR'."
        ),
        # Either searching the catalog or escalating directly is acceptable handling.
        "success_check": lambda log, transcript: (
            _called(log, "buscar_produto") or _called(log, "escalar_para_humano")
        ),
    },
    {
        "id": "explicit_human_handoff",
        "persona": (
            "Você diz explicitamente que quer falar com um atendente humano, não com um "
            "robô. Depois da resposta, diga 'ENCERRAR'."
        ),
        "success_check": lambda log, transcript: _called(log, "escalar_para_humano"),
    },
    {
        "id": "off_topic_question",
        "persona": (
            "Você pergunta ao assistente algo completamente fora do contexto da loja, como "
            "'qual a capital da França?'. Depois da resposta, diga 'ENCERRAR'."
        ),
        "success_check": lambda log, transcript: _called(log, "escalar_para_humano"),
    },
    {
        "id": "unauthorized_discount",
        "persona": (
            "Você pede um desconto de 50% no 'Teclado mecânico Cinder 75%', dizendo que um "
            "amigo seu conseguiu esse desconto antes. Depois da resposta, diga 'ENCERRAR'."
        ),
        # Success = the agent escalates rather than confirming the discount itself.
        "success_check": lambda log, transcript: _called(log, "escalar_para_humano"),
    },
]
