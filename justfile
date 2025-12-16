start:
    python main.py

lint:
    uv run ruff format --check .
    uv run ruff check .
    uv run basedpyright .
