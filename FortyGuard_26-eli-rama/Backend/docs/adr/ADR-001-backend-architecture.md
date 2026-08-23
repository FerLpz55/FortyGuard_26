# ADR-001: Arquitectura del Backend OmniTherm AI

**Estado:** Aceptado
**Fecha:** 2026-08-20
**Decisores:** Equipo OmniTherm (hackathon FortyGuard)

## Contexto

OmniTherm AI es una plataforma centralizada que actúa como "cerebro térmico" de una empresa, unificando en un Agente Autónomo de IA: predicción de riesgos, eficiencia energética y automatización. El agente consume datos hiperlocales de FortyGuard Temperature API®, los cruza con la operativa de la empresa y actúa en tiempo real.

**Restricciones:**
- Hackathon con deadline de esta semana (3-5 días)
- Equipo en curva de aprendizaje (FastAPI/backend)
- Frontend ya existe (HTML/JS estático: `OmniTherm-front-panel`)
- Lilly ya construyó un pipeline RAG funcional (LangChain + ChromaDB + Gemini)

**Fuerzas en juego:**
1. Velocidad de entrega vs calidad arquitectónica
2. Reutilizar trabajo existente (RAG de Lilly) vs empezar de cero
3. Simplicidad de deploy vs escalabilidad futura

## Decisión

Construir un **modular monolith** con FastAPI, PostgreSQL, SQLAlchemy 2.0 (async), Alembic, y **Google ADK** como framework de agente. Adaptar el RAG de Lilly como tool del agente (no dejarlo como código muerto).

## Opciones Consideradas

### Opción A: Modular Monolith con FastAPI + Google ADK (ELEGIDA)

| Dimensión | Evaluación |
|-----------|------------|
| Complejidad | Baja-Media |
| Costo | Gratis (frameworks Apache/MIT, PaaS free tier) |
| Escalabilidad | Media (deploy single container, escala vertical) |
| Familiaridad | Media (FastAPI estándar, ADK intuitivo) |

**Pros:**
- Un solo deploy (ideal hackathon)
- Separación limpia por capas (models/schemas/repos/services/api/agents)
- ADK gratis (Apache 2.0), governance nativo, multi-agent
- Reutiliza Gemini (ya configurado) y RAG de Lilly

**Cons:**
- Menos flexibilidad que microservicios
- ADK es relativamente nuevo (migración v1→v2)

### Opción B: Microservicios (FastAPI + Kafka + workers separados)

| Dimensión | Evaluación |
|-----------|------------|
| Complejidad | Alta |
| Costo | Alto (infra múltiple) |
| Escalabilidad | Alta |
| Familiaridad | Baja (overkill equipo learning) |

**Pros:** Escalabilidad horizontal, aislamiento fallos.
**Cons:** Demasiado para hackathon, mayor tiempo de setup, infra compleja.

### Opción C: Serverless (Lambda/Functions + API Gateway)

| Dimensión | Evaluación |
|-----------|------------|
| Complejidad | Media |
| Costo | Variable |
| Escalabilidad | Alta (auto) |
| Familiaridad | Baja |

**Pros:** Sin gestión de servidores.
**Cons:** Cold starts afectan al agente (LLM calls), estado/DB complicado, debug difícil.

## Trade-off Analysis

Elegimos **Opción A** porque equilibra velocidad (restricción #1) con calidad (restricción #2). Microservicios y serverless añaden complejidad injustificable para un hackathon. La estructura modular permite extraer servicios a futuro sin reescribir lógica.

## Consecuencias

**Se vuelve más fácil:**
- Deploy con `docker compose up` o push a Railway/Render
- Onboarding del equipo (una base de código, capas claras)
- Demostrar el agente con governance ante jueces
- Reutilizar el RAG de Lilly como ventaja competitiva

**Se vuelve más difícil:**
- Escalar horizontalmente (requiere refactor a futuro)
- Aislar fallos por componente

**Revisitar después del hackathon:**
- Migración de embeddings MiniLM → text-embedding-004 (mejor precisión)
- Extraer scheduler a worker separado si crece el volumen
- Evaluar Vertex AI Agent Engine para producción

## Action Items

1. [x] Documentar arquitectura completa (`docs/architecture/`)
2. [x] Diagrama ER notación Chen
3. [x] Especificación API
4. [x] Arquitectura agente ADK + governance
5. [x] Integración FortyGuard (submit+poll)
6. [x] Adaptación RAG de Lilly
7. [x] Despliegue + CI/CD
8. [ ] Implementar código según docs
9. [ ] Conectar frontend a APIs reales
10. [ ] Deploy y demo
