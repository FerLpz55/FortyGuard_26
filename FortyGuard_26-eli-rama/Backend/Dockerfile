# =============================================================================
# OmniTherm API — Multi-stage Docker build
# Stage 1: Build dependencies in a throwaway layer
# Stage 2: Slim runtime with only what's needed
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# System dependencies for building Python packages (asyncpg, bcrypt, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverages Docker layer caching)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# ---- Runtime stage ----
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Non-root user for security (OWASP A05 — Security Misconfiguration)
RUN useradd --no-create-home --shell /bin/false omnitherm
USER omnitherm

EXPOSE 8000

# Health check to verify the container is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
