# Multi-stage Dockerfile for nanobot gateway
# Adapted from backend/Dockerfile pattern

# ---
# Stage 1: Build the application
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads, use system interpreter
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace root for MCP and webchat access
COPY --from=workspace pyproject.toml uv.lock /app/
COPY nanobot/pyproject.toml /app/nanobot/pyproject.toml
COPY mcp/pyproject.toml /app/mcp/pyproject.toml
COPY nanobot-websocket-channel/nanobot_webchat/pyproject.toml /app/nanobot-websocket-channel/nanobot_webchat/pyproject.toml

# Sync nanobot package (includes lms-mcp from workspace)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot

# Copy the nanobot source code
COPY nanobot /app/nanobot

# Copy MCP source code (needed for editable install)
COPY mcp /app/mcp

# Copy webchat channel source code
COPY nanobot-websocket-channel /app/nanobot-websocket-channel

# Final sync with all packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

# ---
# Stage 2: Final runtime image
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Create non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/nanobot"

# Use non-root user
USER nonroot

WORKDIR /app/nanobot

# Run the nanobot gateway via entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
