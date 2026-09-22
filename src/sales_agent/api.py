"""FastAPI service exposing the customer and internal agents as chat endpoints."""

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

from openai import OpenAI  # noqa: E402

from sales_agent.agent import run_customer_agent, run_internal_agent  # noqa: E402
from sales_agent.crm import CRM  # noqa: E402

app = FastAPI(title="Sales Agent")
_crm = CRM()
_client = OpenAI()


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat/customer")
def chat_customer(req: ChatRequest) -> dict:
    history = _crm.get_history(req.session_id)
    _crm.log_message(req.session_id, "user", req.message)
    run = run_customer_agent(_client, _crm, history, req.message)
    _crm.log_message(req.session_id, "assistant", run.final_text)
    return {"reply": run.final_text, "tool_calls": run.tool_calls_log}


@app.post("/chat/internal")
def chat_internal(req: ChatRequest) -> dict:
    history = _crm.get_history(f"internal::{req.session_id}")
    _crm.log_message(f"internal::{req.session_id}", "user", req.message)
    run = run_internal_agent(_client, _crm, history, req.message)
    _crm.log_message(f"internal::{req.session_id}", "assistant", run.final_text)
    return {"reply": run.final_text, "tool_calls": run.tool_calls_log}
