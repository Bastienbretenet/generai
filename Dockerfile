FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync --frozen --no-dev

COPY src/ ./src/

EXPOSE 8088

CMD ["uv", "run", "fastapi", "run", "src/main.py", "--port", "8088"]