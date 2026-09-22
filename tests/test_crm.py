from sales_agent.crm import CRM


def test_register_and_list_lead(tmp_path):
    crm = CRM(tmp_path / "test.db")
    lead_id = crm.register_lead("Ana", "ana@example.com", "cadeira ergonômica")
    leads = crm.list_leads()
    assert len(leads) == 1
    assert leads[0]["id"] == lead_id
    assert leads[0]["status"] == "novo"


def test_schedule_followup_updates_status(tmp_path):
    crm = CRM(tmp_path / "test.db")
    lead_id = crm.register_lead("Bruno", "11999999999")
    crm.schedule_followup(lead_id, "25/12/2026", "10:00")
    leads = crm.list_leads()
    assert leads[0]["status"] == "agendado"


def test_metrics_counts_correctly(tmp_path):
    crm = CRM(tmp_path / "test.db")
    lead_a = crm.register_lead("Ana", "a@example.com")
    crm.register_lead("Bruno", "b@example.com")
    crm.schedule_followup(lead_a, "25/12/2026", "10:00")

    metrics = crm.metrics()
    assert metrics["total_leads"] == 2
    assert metrics["total_appointments"] == 1
    assert metrics["leads_by_status"]["agendado"] == 1
    assert metrics["leads_by_status"]["novo"] == 1


def test_message_history_ordered(tmp_path):
    crm = CRM(tmp_path / "test.db")
    crm.log_message("s1", "user", "oi")
    crm.log_message("s1", "assistant", "olá!")
    crm.log_message("s2", "user", "outra sessão")

    history = crm.get_history("s1")
    assert [m["content"] for m in history] == ["oi", "olá!"]
