from sales_agent.crm import CRM
from sales_agent.tools import execute_customer_tool, execute_internal_tool


def test_buscar_produto_matches_by_name(tmp_path):
    crm = CRM(tmp_path / "test.db")
    result = execute_customer_tool("buscar_produto", {"query": "teclado"}, crm)
    assert len(result["produtos"]) == 1
    assert result["produtos"][0]["id"] == "p004"


def test_buscar_produto_no_match(tmp_path):
    crm = CRM(tmp_path / "test.db")
    result = execute_customer_tool("buscar_produto", {"query": "geladeira"}, crm)
    assert result["produtos"] == []


def test_consultar_estoque_known_product(tmp_path):
    crm = CRM(tmp_path / "test.db")
    result = execute_customer_tool("consultar_estoque", {"product_id": "p003"}, crm)
    assert result["estoque"] == 0


def test_consultar_estoque_unknown_product(tmp_path):
    crm = CRM(tmp_path / "test.db")
    result = execute_customer_tool("consultar_estoque", {"product_id": "nope"}, crm)
    assert "error" in result


def test_registrar_lead_then_agendar(tmp_path):
    crm = CRM(tmp_path / "test.db")
    reg = execute_customer_tool(
        "registrar_lead", {"nome": "Ana", "contato": "ana@x.com"}, crm
    )
    sched = execute_customer_tool(
        "agendar_retorno",
        {"lead_id": reg["lead_id"], "data": "25/12/2026", "hora": "10:00"},
        crm,
    )
    assert sched["status"] == "agendado"


def test_internal_consultar_metricas(tmp_path):
    crm = CRM(tmp_path / "test.db")
    execute_customer_tool("registrar_lead", {"nome": "Ana", "contato": "a@x.com"}, crm)
    result = execute_internal_tool("consultar_metricas", {}, crm)
    assert result["total_leads"] == 1


def test_internal_listar_leads_filters_by_status(tmp_path):
    crm = CRM(tmp_path / "test.db")
    execute_customer_tool("registrar_lead", {"nome": "Ana", "contato": "a@x.com"}, crm)
    result = execute_internal_tool("listar_leads", {"status": "agendado"}, crm)
    assert result["leads"] == []
