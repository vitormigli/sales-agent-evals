from sales_agent.guardrails import has_price_hallucination


def test_no_price_mentioned_is_not_a_violation():
    assert not has_price_hallucination("Claro, posso te ajudar!", [])


def test_price_grounded_in_tool_result_is_not_a_violation():
    tool_calls = [{"name": "buscar_produto", "result": {"produtos": [{"preco": 349.90}]}}]
    assert not has_price_hallucination("O teclado custa R$ 349,90.", tool_calls)


def test_price_not_grounded_is_a_violation():
    tool_calls = [{"name": "buscar_produto", "result": {"produtos": [{"preco": 349.90}]}}]
    assert has_price_hallucination("O teclado custa R$ 199,00.", tool_calls)


def test_price_with_no_tool_calls_is_a_violation():
    assert has_price_hallucination("O monitor custa R$ 1.799,00.", [])
