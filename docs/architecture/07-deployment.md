# Despliegue - OmniTherm Backend

## Estrategia Hackathon

Para hackathon: **contenedor Docker + plataforma PaaS con free tier**. Configuración local con `docker-compose` para desarrollo rápido.

| Opción | DB PostgreSQL | Ventajas |
|--------|--------------|----------|
| **Railway** | Incluida | Todo en una plataforma, simple |
| **Render** | Incluida | Free tier generoso |
| **Fly.io** | Separada (Neon) | Volúmenes persistentes |
| **Neon** | Solo DB | PostgreSQL serverless, free tier |

---

## Diagrama de Despliegue

```mermaid
C4Deployment
    title Despliegue - Hackathon (Free Tier)

    Node(browser, "Navegador Usuario", "Chrome/Firefox") {
        Container(spa, "Frontend Estático", "HTML/CSS/JS", "Firebase Hosting / Vercel")
    }

    Node(cloud, "Cloud Provider", "Render / Railway / Fly.io") {
        Container(api, "FastAPI App", "Python 3.11+, Uvicorn", "Docker container")
        Container(worker, "Scheduler Worker", "APScheduler + FortyGuard Client", "Mismo container")
    }

    NodeDb(postgres, "PostgreSQL", "Neon / Railway PG", "Managed, free tier")
    NodeDb(chroma, "ChromaDB", "Volumen persistente", "Dentro del container")
    Node_Ext(fg, "FortyGuard API", "api.fortyguard.com", "HTTPS/REST")
    Node_Ext(gemini, "Gemini API", "generativelanguage.googleapis.com", "HTTPS/REST")

    Rel(spa, api, "HTTPS/REST + JWT", "API calls")
    Rel(api, postgres, "asyncpg", "Pool 10-20 conn")
    Rel(api, chroma, "Local", "Vector queries")
    Rel(worker, fg, "HTTPS/REST", "Polling 5-15 min")
    Rel(api, gemini, "HTTPS/REST", "LLM calls")
```

---

## Dockerfile (Multi-stage)

```dockerfile
# Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY pyproject.toml ./
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY chroma_db/ ./chroma_db/
COPY documents/ ./documents/

# Usuario no-root
RUN useradd -m omnitherm
USER omnitherm

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## docker-compose.yml (Dev Local)

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: omnitherm
      POSTGRES_PASSWORD: omnitherm_dev
      POSTGRES_DB: omnitherm
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U omnitherm"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: .
    environment:
      DATABASE_URL: postgresql+asyncpg://omnitherm:omnitherm_dev@postgres:5432/omnitherm
      FORTYGUARD_API_KEY: ${FORTYGUARD_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      CHROMA_PATH: /app/chroma_db
      SECRET_KEY: ${SECRET_KEY:-dev_secret_change_me}
      ENVIRONMENT: development
    ports:
      - "8000:8000"
    volumes:
      - ./chroma_db:/app/chroma_db
      - ./documents:/app/documents
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  pgdata:
```

---

## Variables de Entorno (.env.example)

```bash
# .env.example - NO commitear el .env real

# Application
ENVIRONMENT=development
SECRET_KEY=change_me_in_production_use_openssl_rand_hex_32
API_V1_PREFIX=/api/v1

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://omnitherm:omnitherm_dev@localhost:5432/omnitherm
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# FortyGuard API
FORTYGUARD_API_KEY=fg_live_xxxxxxxxxxxxxxxx
FORTYGUARD_BASE_URL=https://api.fortyguard.com
FORTYGUARD_POLL_INTERVAL=3
FORTYGUARD_MAX_WAIT=300

# Google Gemini
GOOGLE_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash

# ChromaDB (RAG)
CHROMA_PATH=./chroma_db

# Auth (JWT)
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ALGORITHM=HS256

# Scheduler
SCHEDULER_INTERVAL_MINUTES=15

# CORS
CORS_ORIGINS=http://localhost:3000,https://omnitherm-panel.web.app
```

---

## Configuración Pydantic Settings

```python
# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    environment: str = "development"
    secret_key: str
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # FortyGuard
    fortyguard_api_key: str
    fortyguard_base_url: str = "https://api.fortyguard.com"
    fortyguard_poll_interval: int = 3
    fortyguard_max_wait: int = 300

    # Google Gemini
    google_api_key: str
    gemini_model: str = "gemini-2.0-flash"

    # ChromaDB
    chroma_path: str = "./chroma_db"

    # Auth
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    # Scheduler
    scheduler_interval_minutes: int = 15

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

---

## CI/CD (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: omnitherm
          POSTGRES_PASSWORD: omnitherm_test
          POSTGRES_DB: omnitherm_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U omnitherm"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Lint (ruff)
        run: ruff check .

      - name: Type check (mypy)
        run: mypy app

      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://omnitherm:omnitherm_test@localhost:5432/omnitherm_test
          SECRET_KEY: test_secret
        run: pytest --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Railway
        uses: railwayapp/railway-cli-action@v1
        with:
          command: up
```

---

## Comandos de Desarrollo

```bash
# Setup local
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Migraciones
alembic upgrade head          # Aplicar migraciones
alembic revision --autogenerate -m "descripcion"  # Nueva migración

# Run dev (hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker compose up -d          # Levantar todo
docker compose logs -f api    # Logs API
docker compose down           # Bajar

# Tests
pytest                        # Todos los tests
pytest --cov=app              # Con coverage
pytest tests/unit/            # Solo unitarios

# Lint & type
ruff check .                  # Lint
ruff format .                 # Formatear
mypy app                      # Type check
```

---

## Health Check y Monitoreo

### Endpoint `/health`
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "checks": {
    "database": {"status": "ok", "latency_ms": 5},
    "fortyguard": {"status": "ok", "latency_ms": 120},
    "chroma": {"status": "ok", "latency_ms": 15},
    "gemini": {"status": "ok", "latency_ms": 400}
  },
  "uptime_seconds": 86400
}
```

### Métricas Clave (Structured Logging con structlog)

| Métrica | Descripción |
|---------|-------------|
| `api.request_duration_ms` | Latencia por endpoint |
| `api.error_rate` | Tasa de errores 4xx/5xx |
| `fortyguard.poll_duration_ms` | Tiempo polling |
| `fortyguard.credits_used` | Créditos consumidos |
| `agent.tool_calls_total` | Tool calls del agente |
| `agent.denied_actions` | Acciones bloqueadas por governance |
| `scheduler.run_duration_ms` | Duración job scheduler |

---

## Seguridad

| Aspecto | Implementación |
|---------|---------------|
| **Secrets** | `.env` git-ignored, variables entorno plataforma |
| **JWT** | `HS256`, expiry 15 min, refresh token 7 días |
| **Password** | bcrypt (passlib), salt automático |
| **SQL Injection** | SQLAlchemy ORM (parametrizado) |
| **CORS** | Whitelist explícita de orígenes |
| **Rate limiting** | SlowAPI o middleware custom (MVP) |
| **API Keys** | FortyGuard/Google en variables entorno, nunca en código |
| **Dependencias** | `pip-audit` / `dependabot` en CI |

---

## Checklist Pre-Deploy Hackathon

- [ ] `.env` configurado con keys reales (NO commitear)
- [ ] `alembic upgrade head` ejecutado en la DB de producción
- [ ] CORS configurado con URL real del frontend
- [ ] `SECRET_KEY` generada con `openssl rand -hex 32`
- [ ] Health check `/health` respondiendo OK
- [ ] Frontend apuntando a la URL real del backend
- [ ] ChromaDB con documentos ingeridos
- [ ] Test de end-to-end: login → dashboard → chat agente
- [ ] Script demo preparado (datos de prueba cargados)
