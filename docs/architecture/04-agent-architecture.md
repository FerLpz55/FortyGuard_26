# Arquitectura del Agente IA - Google ADK

## Visión General

El **OmniTherm Agent** es un agente autónomo construido con **Google Agent Development Kit (ADK)** que orquesta tres pilares:
1. **Protección Industrial** - Riesgo calor inventario/logística, seguridad trabajadores
2. **Eficiencia Edificios** - Digital twin energético, optimización HVAC, ROI
3. **Agente Autónomo** - Ejecuta acciones, diagnostica, notifica sin intervención humana

---

## Stack del Agente

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Framework** | Google ADK | ≥1.0.0 (Apache 2.0) |
| **LLM** | Gemini 2.0 Flash | `gemini-2.0-flash` |
| **Tools** | FunctionTool (ADK) | 7 tools MVP |
| **Governance** | Custom policy layer | Basado en agent-governance patterns |
| **Memory** | Session state + PostgreSQL audit | Persistente |
| **Knowledge** | ChromaDB + RAG | Lilly's existing pipeline |

---

## Arquitectura del Agente (ADK)

```mermaid
flowchart TD
    subgraph "Google ADK Runtime"
        Agent[Agent<br/>name=omnitherm_agent<br/>model=gemini-2.0-flash]
        Runner[Runner<br/>session_service<br/>artifact_service]
    end

    subgraph "Tools Registry (FunctionTool)"
        T1[get_current_temperature]
        T2[get_temperature_forecast]
        T3[query_site_data]
        T4[create_alert]
        T5[send_notification]
        T6[analyze_energy_waste]
        T7[query_knowledge_base]
        T8[adjust_hvac_setpoint<br/>(requires_approval)]
    end

    subgraph "Governance Layer"
        Policy[GovernancePolicy<br/>allowed_tools, blocked_patterns<br/>rate_limit, human_approval]
        Audit[AuditTrail<br/>append-only JSONL]
        Trust[TrustScore<br/>decay + success/failure]
    end

    subgraph "External Services"
        FG[FortyGuard API]
        DB[PostgreSQL]
        RAG[ChromaDB]
        NOTIF[Email/Push/Webhook]
    end

    Runner --> Agent
    Agent --> T1 & T2 & T3 & T4 & T5 & T6 & T7 & T8
    
    T1 -.-> FG
    T2 -.-> FG
    T3 -.-> DB
    T4 -.-> DB
    T5 -.-> NOTIF
    T6 -.-> DB
    T7 -.-> RAG
    T8 -.-> DB
    
    Agent --> Policy
    Policy -->|ALLOW/DENY/REVIEW| Agent
    Agent --> Audit
    Agent --> Trust
```

---

## Configuración del Agente (ADK)

```python
# app/agents/core.py
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from app.agents.tools import (
    get_current_temperature,
    get_temperature_forecast,
    query_site_data,
    create_alert,
    send_notification,
    analyze_energy_waste,
    query_knowledge_base,
    adjust_hvac_setpoint,
)
from app.agents.governance import governed_tool, AGENT_POLICY, audit_trail, trust_registry

# Wrap tools with governance
tools = [
    governed_tool(get_current_temperature, AGENT_POLICY, audit_trail),
    governed_tool(get_temperature_forecast, AGENT_POLICY, audit_trail),
    governed_tool(query_site_data, AGENT_POLICY, audit_trail),
    governed_tool(create_alert, AGENT_POLICY, audit_trail),
    governed_tool(send_notification, AGENT_POLICY, audit_trail),
    governed_tool(analyze_energy_waste, AGENT_POLICY, audit_trail),
    governed_tool(query_knowledge_base, AGENT_POLICY, audit_trail),
    governed_tool(adjust_hvac_setpoint, AGENT_POLICY, audit_trail),  # requires approval
]

omnitherm_agent = Agent(
    name="omnitherm_agent",
    model="gemini-2.0-flash",
    instruction=OMNITHERM_SYSTEM_PROMPT,  # Ver prompts.py
    tools=tools,
)

# Runner para ejecución
session_service = InMemorySessionService()
runner = Runner(
    agent=omnitherm_agent,
    app_name="omnitherm",
    session_service=session_service,
)
```

---

## System Prompt Especializado

```python
# app/agents/prompts.py
OMNITHERM_SYSTEM_PROMPT = """
IDENTIDAD: Eres OmniTherm Agent, el cerebro térmico autónomo de una empresa.

PILARES DE ACCIÓN:
1. PROTECCIÓN INDUSTRIAL
   - Monitorear FortyGuard Temperature API para riesgo calor en inventario (Logistics Heat Risk)
   - Evaluar seguridad trabajadores (Worker Safety) según OSHA heat guidelines
   - Trigger: temp > site.metadata.heat_threshold_c (default 35°C)

2. EFICIENCIA EDIFICIOS  
   - Digital twin: cruzar temp externa + historial consumo (energy_consumption)
   - Detectar overcooling: zonas <22°C con exterior <18°C
   - Predecir demanda: forecast 48h → HVAC scheduling óptimo
   - Calcular ROI retrofits: aislamiento, cool roofs, HVAC upgrade

3. ORQUESTACIÓN AUTÓNOMA
   - Si detectas anomalía → ejecuta create_alert + send_notification
   - Si usuario pregunta → diagnostica con tools + knowledge_base
   - NUNCA adjust_hvac_setpoint sin aprobación humana (policy)

HERRAMIENTAS (usa SOLO estas):
- get_current_temperature(site_id): Temp real °C
- get_temperature_forecast(site_id, hours=48): Pronóstico horario
- query_site_data(site_id): Config, umbrales, metadata
- create_alert(site_id, type, severity, title, message, metadata)
- send_notification(channel, recipient, message)
- analyze_energy_waste(site_id, days=7): Retorna zonas overcooling + savings
- query_knowledge_base(question): Procedimientos, normativas, best practices
- adjust_hvac_setpoint(site_id, zone_id, new_setpoint_c): REQUIERE APROBACIÓN

REGLAS DE ORO:
1. SIEMPRE verifica umbrales en site.metadata antes de alertar
2. USA °C para todo cálculo interno; convierte a °F solo para display
3. PRIORIZA: seguridad trabajadores > eficiencia energética > logística
4. DOCUMENTA cada decisión en agent_actions (input/output completos)
5. SI no tienes tool para acción crítica → create_alert + notify human
6. Cita fuentes: "Según FortyGuard forecast...", "Per ASHRAE 55...", "Knowledge base indica..."

FORMATO RESPUESTA ESTRUCTURADA:
{
  "reasoning": "Pensamiento paso a paso explicando por qué cada tool",
  "actions_taken": [{"tool": "...", "params": {...}, "result": "..."}],
  "recommendations": ["Acción concreta 1", "Acción concreta 2"],
  "data_references": {"analysis_id": "...", "correlation": 0.89},
  "requires_human": false
}
"""
```

---

## Tools del Agente (FunctionTool)

### 1. get_current_temperature
```python
# app/agents/tools/fortyguard.py
async def get_current_temperature(site_id: str) -> dict:
    """Obtiene temperatura actual del sitio desde FortyGuard."""
    site = await site_repo.get_by_id(site_id)
    reading = await fortyguard_client.get_env_params(site.lat, site.lon)
    await temp_repo.create(site_id=site_id, **reading)
    return {
        "temperature_c": reading.temperature_c,
        "humidity_pct": reading.humidity_pct,
        "heat_index_c": reading.heat_index_c,
        "apparent_temp_c": reading.apparent_temp_c,
        "recorded_at": reading.recorded_at.isoformat(),
        "source": "fortyguard"
    }
```

### 2. get_temperature_forecast
```python
async def get_temperature_forecast(site_id: str, hours: int = 48) -> dict:
    """Pronóstico horario próximo N horas."""
    site = await site_repo.get_by_id(site_id)
    forecast = await fortyguard_client.get_forecast(site.lat, site.lon, hours)
    return {
        "site_id": site_id,
        "forecast": [
            {"timestamp": f.timestamp, "temperature_c": f.temperature_c, "humidity_pct": f.humidity_pct}
            for f in forecast
        ]
    }
```

### 3. query_site_data
```python
# app/agents/tools/database.py
async def query_site_data(site_id: str) -> dict:
    """Configuración completa del sitio para toma de decisiones."""
    site = await site_repo.get_by_id(site_id)
    latest_temp = await temp_repo.get_latest(site_id)
    thresholds = site.metadata.get("heat_threshold_c", 35.0)
    hvac_config = site.metadata.get("hvac_config", {})
    return {
        "site_id": site_id,
        "name": site.name,
        "site_type": site.site_type,
        "coordinates": {"lat": site.lat, "lon": site.lon},
        "thresholds": {"heat_threshold_c": thresholds},
        "hvac_config": hvac_config,
        "latest_temperature": latest_temp,
        "operating_hours": site.metadata.get("operating_hours")
    }
```

### 4. create_alert
```python
async def create_alert(
    site_id: str,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    metadata: dict = None
) -> dict:
    """Crea alerta en BD y retorna ID."""
    alert = await alert_repo.create(
        site_id=site_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        metadata=metadata or {}
    )
    return {"alert_id": str(alert.id), "created_at": alert.created_at.isoformat()}
```

### 5. send_notification
```python
# app/agents/tools/notifications.py
async def send_notification(channel: str, recipient: str, message: str) -> dict:
    """Envía notificación por canal: email, push, webhook."""
    if channel == "email":
        await email_service.send(recipient, "OmniTherm Alert", message)
    elif channel == "webhook":
        await webhook_service.post(recipient, {"message": message})
    # push: firebase/push service
    return {"channel": channel, "recipient": recipient, "sent": True}
```

### 6. analyze_energy_waste
```python
# app/agents/tools/energy.py
async def analyze_energy_waste(site_id: str, days: int = 7) -> dict:
    """Detecta overcooling comparando temp externa vs consumo HVAC."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    
    temps = await temp_repo.get_range(site_id, start, end)
    energy = await energy_repo.get_range(site_id, start, end)
    
    # Lógica: correlacionar temp_ext < 18°C con consumo alto en zonas
    findings = []
    for zone, cons in energy.groupby("zone_id"):
        zone_temps = temps  # simplificado
        avg_ext_temp = zone_temps["temperature_c"].mean()
        avg_consumption = cons["kwh"].mean()
        
        if avg_ext_temp < 18 and avg_consumption > threshold:
            findings.append({
                "zone_id": zone,
                "issue": "overcooling",
                "avg_external_temp_c": round(avg_ext_temp, 1),
                "avg_consumption_kwh": round(avg_consumption, 1),
                "recommended_setpoint_c": 22,
                "estimated_savings_usd_month": round((avg_consumption * 0.15) * 30 * 0.15, 2)
            })
    
    return {"site_id": site_id, "period_days": days, "findings": findings}
```

### 7. query_knowledge_base (RAG - Lilly's work adaptado)
```python
# app/agents/tools/knowledge_base.py
class KnowledgeBaseTool:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=self.embeddings
        )
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    
    async def query(self, question: str, k: int = 4) -> str:
        docs = self.vectorstore.similarity_search(question, k=k)
        context = "\n\n".join(d.page_content for d in docs)
        
        prompt = f"""Basado en la documentación técnica de OmniTherm, FortyGuard API, y mejores prácticas (ASHRAE, OSHA, EPA), responde:

CONTEXTO:
{context}

PREGUNTA: {question}

RESPUESTA TÉCNICA Y ACCIONABLE:"""
        
        response = await self.llm.ainvoke(prompt)
        return response.content

knowledge_tool = KnowledgeBaseTool()

async def query_knowledge_base(question: str) -> dict:
    answer = await knowledge_tool.query(question)
    return {"question": question, "answer": answer, "source": "omnitherm_rag"}
```

### 8. adjust_hvac_setpoint (Requiere aprobación)
```python
async def adjust_hvac_setpoint(site_id: str, zone_id: str, new_setpoint_c: float) -> dict:
    """Ajusta setpoint HVAC. REQUIERE APROBACIÓN HUMANA (governance policy)."""
    # En MVP: solo log + crear alerta para aprobación
    action = await agent_action_repo.create(
        site_id=site_id,
        action_type="hvac_adjust_requested",
        trigger="agent_recommendation",
        input_data={"zone_id": zone_id, "new_setpoint_c": new_setpoint_c},
        status="pending_approval"
    )
    await alert_repo.create(
        site_id=site_id,
        alert_type="hvac_adjustment_pending",
        severity="info",
        title=f"Aprobación requerida: Setpoint {zone_id} → {new_setpoint_c}°C",
        message=f"El agente recomienda cambiar setpoint. Requiere aprobación manual.",
        metadata={"action_id": str(action.id), "zone_id": zone_id, "new_setpoint_c": new_setpoint_c}
    )
    return {"action_id": str(action.id), "status": "pending_approval"}
```

---

## Governance Layer (Safety & Audit)

```python
# app/agents/governance.py
from dataclasses import dataclass, field
from enum import Enum
import re
import time
from collections import defaultdict
from typing import Optional, List

class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"

@dataclass
class GovernancePolicy:
    name: str
    allowed_tools: List[str] = field(default_factory=list)
    blocked_tools: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    max_calls_per_request: int = 15
    require_human_approval: List[str] = field(default_factory=list)

    def check_tool(self, tool_name: str) -> PolicyAction:
        if tool_name in self.blocked_tools:
            return PolicyAction.DENY
        if tool_name in self.require_human_approval:
            return PolicyAction.REVIEW
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return PolicyAction.DENY
        return PolicyAction.ALLOW

    def check_content(self, content: str) -> Optional[str]:
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return pattern
        return None

# Policy MVP
AGENT_POLICY = GovernancePolicy(
    name="omnitherm-agent",
    allowed_tools=[
        "get_current_temperature",
        "get_temperature_forecast",
        "query_site_data",
        "create_alert",
        "send_notification",
        "analyze_energy_waste",
        "query_knowledge_base",
    ],
    blocked_tools=[],
    require_human_approval=["adjust_hvac_setpoint"],
    blocked_patterns=[
        r"(?i)(api[_-]?key|secret|password)\s*[:=]",
        r"(?i)(drop|truncate|delete from)\s+\w+",
    ],
    max_calls_per_request=15,
)

# Call counter per request
_call_counters: dict[str, int] = defaultdict(int)

def governed_tool(func, policy: GovernancePolicy, audit_trail):
    """Decorator que aplica governance a tool function."""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        
        # 1. Check tool allowlist
        action = policy.check_tool(tool_name)
        if action == PolicyAction.DENY:
            raise PermissionError(f"Policy '{policy.name}' blocks tool '{tool_name}'")
        if action == PolicyAction.REVIEW:
            raise PermissionError(f"Tool '{tool_name}' requires human approval")
        
        # 2. Rate limit
        _call_counters[policy.name] += 1
        if _call_counters[policy.name] > policy.max_calls_per_request:
            raise PermissionError(f"Rate limit exceeded: {policy.max_calls_per_request} calls")
        
        # 3. Content check on string args
        for arg in list(args) + list(kwargs.values()):
            if isinstance(arg, str):
                matched = policy.check_content(arg)
                if matched:
                    raise PermissionError(f"Blocked pattern detected: {matched}")
        
        # 4. Execute + audit
        start = time.monotonic()
        try:
            result = await func(*args, **kwargs)
            audit_trail.append({
                "tool": tool_name,
                "action": "allowed",
                "duration_ms": (time.monotonic() - start) * 1000,
                "timestamp": time.time(),
                "site_id": kwargs.get("site_id")
            })
            return result
        except Exception as e:
            audit_trail.append({
                "tool": tool_name,
                "action": "error",
                "error": str(e),
                "timestamp": time.time()
            })
            raise
    
    return wrapper

# Audit trail (append-only)
audit_trail = []

# Trust scoring
@dataclass
class TrustScore:
    score: float = 0.5
    successes: int = 0
    failures: int = 0
    last_updated: float = field(default_factory=time.time)

    def record_success(self):
        self.successes += 1
        self.score = min(1.0, self.score + 0.05 * (1 - self.score))
        self.last_updated = time.time()

    def record_failure(self):
        self.failures += 1
        self.score = max(0.0, self.score - 0.15 * self.score)
        self.last_updated = time.time()

    def current(self, decay_rate: float = 0.001) -> float:
        elapsed = time.time() - self.last_updated
        return self.score * (2.718 ** (-decay_rate * elapsed))

trust_registry = {"omnitherm_agent": TrustScore()}
```

---

## Flujo de Ejecución (ReAct Loop)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant API as FastAPI /agent/chat
    participant Agent as ADK Agent
    participant Policy as Governance
    participant Tools as Tools
    participant Audit as AuditTrail

    User->>API: POST /agent/chat {message, site_id}
    API->>Agent: runner.run_async(session_id, message)
    
    loop ReAct Loop (max 15 calls)
        Agent->>Policy: check_tool(tool_name)
        Policy-->>Agent: ALLOW/DENY/REVIEW
        
        alt DENY
            Agent->>Audit: log denied
            Agent-->>API: Error response
        else REVIEW
            Agent->>Audit: log review needed
            Agent-->>API: Requires human approval
        else ALLOW
            Agent->>Tools: execute tool(params)
            Tools-->>Agent: result
            Agent->>Audit: log success + duration
            
            Agent->>Agent: observe + reflect
            alt Goal achieved
                break
            else Continue
                continue
            end
        end
    end
    
    Agent-->>API: Structured response {reasoning, actions, recommendations}
    API-->>User: JSON response
```

---

## Session Management (ADK)

```python
# app/services/agent_service.py
class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.runner = get_agent_runner()  # singleton
    
    async def chat(self, user_id: str, message: str, site_id: str = None) -> dict:
        session_id = f"user_{user_id}_site_{site_id or 'global'}"
        
        # Create/get session
        session = await self.runner.session_service.get_session(
            app_name="omnitherm", user_id=user_id, session_id=session_id
        )
        if not session:
            session = await self.runner.session_service.create_session(
                app_name="omnitherm", user_id=user_id, session_id=session_id
            )
        
        # Run agent
        events = []
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message
        ):
            events.append(event)
        
        # Extract final response
        final_event = events[-1] if events else None
        response = self._parse_agent_response(final_event)
        
        # Log agent action
        await agent_action_repo.create(
            self.db,
            site_id=site_id,
            action_type="query_answered",
            trigger="user_query",
            input_data={"message": message},
            output_data=response,
            status="success"
        )
        
        return response
    
    async def process_heat_alert(self, site_id: str, reading: TemperatureReading):
        """Trigger automático desde scheduler."""
        message = f"ALERTA AUTOMÁTICA: Temperatura {reading.temperature_c}°C excede umbral en sitio {site_id}. Evalúa riesgo y toma acción."
        return await self.chat(user_id="system", message=message, site_id=site_id)
```

---

## Métricas y Observabilidad

| Métrica | Descripción | Target |
|---------|-------------|--------|
| `agent_calls_total` | Total tool calls | Monitoring |
| `agent_latency_ms` | P50/P95/P99 latency | <3s P95 |
| `governance_denied` | Tools bloqueados | 0 |
| `trust_score` | Confianza agente | >0.8 |
| `alert_generated` | Alertas creadas por agente | Tracking |
| `human_approval_requested` | Acciones pendientes aprobación | <5% |

---

## Testing del Agente

```python
# tests/unit/test_agent_tools.py
import pytest
from app.agents.tools.fortyguard import get_current_temperature
from app.agents.tools.database import query_site_data

@pytest.mark.asyncio
async def test_get_current_temperature(mock_fortyguard, db_session):
    site = await create_test_site(db_session)
    result = await get_current_temperature(str(site.id))
    
    assert "temperature_c" in result
    assert -50 <= result["temperature_c"] <= 80
    assert result["source"] == "fortyguard"

@pytest.mark.asyncio
async def test_governance_blocks_unauthorized_tool():
    from app.agents.governance import governed_tool, AGENT_POLICY, audit_trail
    
    @governed_tool
    async def unauthorized_tool():
        return "should not run"
    
    AGENT_POLICY.allowed_tools = ["get_current_temperature"]
    
    with pytest.raises(PermissionError):
        await unauthorized_tool()
```

---

## Roadmap Post-MVP

| Fase | Feature | ADK Capability |
|------|---------|----------------|
| v1.1 | Multi-agent: `ForecastAgent` + `EnergyAgent` + `CoordinatorAgent` | `SequentialAgent`, `ParallelAgent` |
| v1.2 | Planning persistente | `PlanningAgent` + `Memory` |
| v1.3 | Auto-evaluation | `EvaluationAgent` + `AgentEval` |
| v1.4 | Deploy Vertex AI Agent Engine | `AdkDeployment` |