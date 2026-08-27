FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev

COPY config.yaml ./
COPY artifacts ./artifacts
COPY data ./data

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "factorypulse", "serve"]

