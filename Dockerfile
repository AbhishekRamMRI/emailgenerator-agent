FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN pip install --no-cache-dir uv

RUN uv sync --frozen --no-dev

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uv", "run", "--no-dev", "python", "-m", "emailgenerator_agent.mcp_server.server"]