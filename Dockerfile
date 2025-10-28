FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY main.py ./
COPY src/ src/
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "python", "main.py"]
