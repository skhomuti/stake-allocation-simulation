# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Install uv (fast Python package manager) for reproducible installs from pyproject/uv.lock
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project metadata first for better layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies into local venv managed by uv
RUN uv sync --no-dev --frozen

# Copy the application code and assets
COPY app ./app
COPY templates ./templates
COPY static ./static
COPY abi ./abi
COPY scripts ./scripts

# Activate venv for runtime
ENV PATH="/app/.venv/bin:$PATH"

# Expose FastAPI default port
EXPOSE 8000

# Common envs (override at runtime)
ENV ETH_RPC_URL="" \
    LIDO_LOCATOR_ADDRESS="" \
    STAKING_ROUTER_ADDRESS="" \
    COMMUNITY_STAKING_MODULE_ADDRESS="" \
    PYTHONPATH="/app"

# Start the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

