# Contexto del Sistema - OmniTherm AI

## Visión General

OmniTherm AI es una plataforma centralizada que actúa como el "cerebro térmico" de una empresa. Unifica predicción de riesgos, eficiencia energética y automatización en un **Agente Autónomo de IA** que consume datos climáticos hiperlocales (FortyGuard Temperature API®), cruza la información con la operativa de la empresa y toma decisiones en tiempo real.

## Actores

| Actor | Descripción | Interacciones |
|-------|-------------|---------------|
| **Usuario/Gerente** | Personal de operaciones, facility managers, directivos | Dashboard web, chat con agente, alertas |
| **Desarrollador** | Integraciones con sistemas propios (ERP, BMS, IoT) | API REST documentada |
| **Scheduler (Sistema)** | Proceso automático periódico | Polling FortyGuard, evaluación umbrales, trigger agente |

## Sistemas Externos

```mermaid
C4Context
    title Contexto del Sistema - OmniTherm AI

    Person(user, "Usuario / Gerente", "Accede al dashboard web para monitorear sitios, ver alertas y chatear con el agente")
    Person(dev, "Desarrollador", "Integra sistemas propios via API REST")

    System(frontend, "Frontend Panel", "HTML/JS estático (OmniTherm-front-panel), servido en Firebase/Vercel")
    System_Boundary(b1, "OmniTherm Backend") {
        System(api, "API Gateway (FastAPI)", "Autenticación, rate limiting, routing, OpenAPI docs")
        System(agent, "AI Agent Core (Google ADK)", "Razonamiento, planificación, ejecución de herramientas, governance")
        SystemDb(db, "PostgreSQL", "Datos persistentes: usuarios, sitios, temperaturas, alertas, energía, auditoría")
        SystemQueue(scheduler, "Scheduler (APScheduler)", "Polling periódico FortyGuard cada 15 min")
    }
    System_Ext(fortyguard, "FortyGuard Temperature API", "API async (submit+poll): heatmaps, env_params, heat_intelligence, segmentación")
    System_Ext(gemini, "Google Gemini API", "LLM para razonamiento del agente (gemini-2.0-flash)")
    System_Ext(chroma, "ChromaDB (RAG)", "Base vectorial conocimiento: procedimientos, normativas, best practices")

    Rel(user, frontend, "HTTPS", "Login, Dashboard, Chat")
    Rel(dev, api, "HTTPS/REST", "Integración sistemas externos")
    Rel(frontend, api, "HTTPS/REST + JWT", "API calls autenticadas")
    Rel(api, agent, "In-process", "Delegación consultas complejas")
    Rel(api, db, "asyncpg", "CRUD entidades")
    Rel(api, scheduler, "In-process", "Trigger jobs")
    Rel(scheduler, fortyguard, "HTTPS/REST", "Polling submit+poll")
    Rel(agent, fortyguard, "HTTPS/REST", "Tools: temp actual, forecast, heatmap")
    Rel(agent, db, "asyncpg", "Tools: query sites, create alerts, energy analysis")
    Rel(agent, gemini, "HTTPS/REST", "Razonamiento LLM")
    Rel(agent, chroma, "gRPC/HTTP", "Tool: knowledge_base query")
    Rel(agent, api, "In-process", "Emitir alertas, notificaciones")
```

## Flujos de Datos Principales

### 1. Monitoreo Automático (Scheduled)
```
Scheduler (15 min) → FortyGuard API (submit+poll) → PostgreSQL (temperature_readings) 
→ Evaluar umbrales → Si excede: Agent.process_heat_alert() → Alertas + Notificaciones
```

### 2. Consulta Usuario (On-Demand)
```
Frontend → API Gateway → Agent.chat() → Tools (FortyGuard, DB, RAG) → Respuesta estructurada
```

### 3. Análisis Eficiencia (Bajo demanda)
```
Usuario/API → Agent.analyze_energy_waste() → DB (energy_consumption + temperature_readings) 
→ LLM reasoning → Recomendaciones HVAC + ROI estimado
```

## Límites del Sistema

| Límite | Detalle |
|--------|---------|
| **Geográfico** | FortyGuard API: Solo Estados Unidos (coordenadas fuera dan error) |
| **Temporal** | Datos históricos: 2021 → hoy. No futuro. |
| **Plan API** | Basic: 10 mi² heatmap, 1M créditos/mes. Premium: 50 mi², 5M créditos, segmentación, heat_intelligence |
| **Concurrencia** | Polling máx 3s intervalo, timeout 5 min por task |
| **Agente** | Máx 15 llamadas tool por request, rate limit por política governance |

## Decisiones Arquitectónicas Clave

| Decisión | Opción | Rationale |
|----------|--------|-----------|
| **Estilo** | Modular Monolith | Simple para hackathon, deploy single container, separación limpia por capas |
| **Agent Framework** | Google ADK | Gratis (Apache 2.0), governance nativo, multi-agent, Gemini nativo |
| **FortyGuard** | Polling 15min + webhook-ready | Sin URL pública necesaria para hackathon, extensible a webhooks |
| **Auth** | JWT stateless | Funciona con frontend estático sin sesiones server-side |
| **Real-time** | Polling frontend 30s | Evita WebSockets, simple para MVP |
| **DB** | PostgreSQL + JSONB | Relacional para integridad, JSONB para metadata flexible (sitios, alertas, acciones) |