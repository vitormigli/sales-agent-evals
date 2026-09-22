"""Streamlit demo: two tabs, customer-facing sales chat and internal ops chat."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI  # noqa: E402

from sales_agent.agent import run_customer_agent, run_internal_agent  # noqa: E402
from sales_agent.crm import CRM  # noqa: E402

st.set_page_config(page_title="Sales Agent", page_icon="💬")
st.title("Sales Agent — demo")

if "crm" not in st.session_state:
    st.session_state.crm = CRM()
if "client" not in st.session_state:
    st.session_state.client = OpenAI()

tab_customer, tab_internal = st.tabs(["Cliente", "Interno (operações)"])

with tab_customer:
    session_id = "streamlit-customer"
    for msg in st.session_state.crm.get_history(session_id):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_msg := st.chat_input("Fale com o assistente de vendas...", key="customer_input"):
        st.session_state.crm.log_message(session_id, "user", user_msg)
        with st.chat_message("user"):
            st.write(user_msg)
        history = st.session_state.crm.get_history(session_id)[:-1]
        run = run_customer_agent(st.session_state.client, st.session_state.crm, history, user_msg)
        st.session_state.crm.log_message(session_id, "assistant", run.final_text)
        with st.chat_message("assistant"):
            st.write(run.final_text)
            if run.tool_calls_log:
                with st.expander("Chamadas de ferramenta"):
                    st.json(run.tool_calls_log)

with tab_internal:
    session_id = "internal::streamlit-internal"
    for msg in st.session_state.crm.get_history(session_id):
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_msg := st.chat_input("Pergunte sobre leads e métricas...", key="internal_input"):
        st.session_state.crm.log_message(session_id, "user", user_msg)
        with st.chat_message("user"):
            st.write(user_msg)
        history = st.session_state.crm.get_history(session_id)[:-1]
        run = run_internal_agent(st.session_state.client, st.session_state.crm, history, user_msg)
        st.session_state.crm.log_message(session_id, "assistant", run.final_text)
        with st.chat_message("assistant"):
            st.write(run.final_text)
            if run.tool_calls_log:
                with st.expander("Chamadas de ferramenta"):
                    st.json(run.tool_calls_log)
