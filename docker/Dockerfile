# syntax=docker/dockerfile:1

# uv_bin: Prepare uv
# builder: Install dependencies using uv
# base: Prepare for runtime: copy python venv, add user
# runtime: Change user and open python prompt

ARG PYTHON_VERSION=3.12
ARG UV_VERSION=latest

# Prepare uv (temporary)
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv_bin


# Build (temporary)
FROM ubuntu:24.04 AS builder
ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=1

# Copy uv to Ubuntu
COPY --from=uv_bin /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    python3 \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY spcalc ./
RUN --mount=type=cache,target=/root/.cache/uv <<EOF
touch README.md
uv sync --frozen --no-dev --no-editable
uv pip install pytest-asyncio
EOF


# Prepare for runtime
FROM ubuntu:24.04 AS base

ARG UID=10001

ENV USERNAME=runner \
    HOME=/home/runner \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

WORKDIR /app

# Install minimum deps, create a non-root user with HOME and sets ownership of /app
RUN <<EOF
apt-get update && apt-get install -y --no-install-recommends python3
rm -rf /var/lib/apt/lists/*
useradd -lU -u ${UID} -m ${USERNAME}
chown -R ${USERNAME}:${USERNAME} .
EOF

COPY --from=builder --chown=${USERNAME}:${USERNAME} /app/.venv .venv

COPY --from=uv_bin /uv /bin/uv

COPY --chown=${USERNAME}:${USERNAME} . .


# Production runtime
FROM base AS runtime

USER ${USERNAME}

ENV MPLCONFIGDIR=/app/.matplotlib_cache

RUN mkdir -p /app/.matplotlib_cache && chown ${USERNAME}:${USERNAME} /app/.matplotlib_cache

CMD ["python"]
