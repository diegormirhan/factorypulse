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

# Hosted platforms assign the port at runtime; PORT overrides config.yaml.
ENV PORT=8000
EXPOSE 8000

RUN useradd --create-home --uid 1001 factorypulse \
    && chown -R factorypulse:factorypulse /app
USER factorypulse

CMD ["uv", "run", "--no-sync", "factorypulse", "serve"]

