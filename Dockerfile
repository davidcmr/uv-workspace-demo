FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY libs/ ./libs/
COPY apps/ ./apps/

RUN uv sync --frozen --no-dev

# DL Archiver Image
FROM base AS dl-archiver
WORKDIR /app
COPY apps/dl-archiver/ ./apps/dl-archiver/
RUN uv sync --frozen --no-dev --project apps/dl-archiver
CMD ["uv", "run", "dl-archiver"]


# DL EFS Cleanup Image
FROM base AS dl-efs-cleanup
WORKDIR /app
COPY apps/dl-efs-cleanup/ ./apps/dl-efs-cleanup/
RUN uv sync --frozen --no-dev --project apps/dl-efs-cleanup
CMD ["uv", "run", "dl-efs-cleanup"]
