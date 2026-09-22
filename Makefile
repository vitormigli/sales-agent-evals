.PHONY: run demo eval test lint

run:
	uv run uvicorn sales_agent.api:app --host 0.0.0.0 --port 8000 --reload

demo:
	uv run streamlit run src/sales_agent/streamlit_app.py

eval:
	uv run python evals/run_eval.py

test:
	uv run pytest

lint:
	uv run ruff check .
