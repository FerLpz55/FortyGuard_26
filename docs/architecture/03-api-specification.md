# Especificación API - OmniTherm Backend

## Convenciones Generales

| Aspecto | Estándar |
|---------|----------|
| **Base URL** | `/api/v1` |
| **Autenticación** | Bearer Token (JWT) en header `Authorization` |
| **Formato** | JSON (request/response) |
| **Fechas** | ISO 8601 UTC (`2026-08-20T14:30:00Z`) |
| **Unidades** | °C interno, °F opcional en response con `?unit=f` |
| **Paginación** | `?page=1&size=20` → `{items, total, page, size, pages}` |
| **Errores** | RFC 7807 Problem Details |

## Esquema de Error Estándar

```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "Validation Error",
  "status": 422,
  "detail": "Invalid input parameters",
  "instance": "/api/v1/sites",
  "errors": [
    {"field": "lat", "message": "Latitude must be between -90 and 90"}
  ]
}
```

Códigos HTTP: `200` OK, `201` Created, `400` Bad Request, `401` Unauthorized, `403` Forbidden, `404` Not Found, `422` Validation Error, `429` Rate Limited, `500` Internal Error.

---

## Autenticación

### POST `/api/v1/auth/login`
**Login con email/password → JWT access + refresh token**

**Request:**
```json
{
  "email": "usuario@empresa.com",
  "password": "password123"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "usuario@empresa.com",
    "full_name": "Juan Pérez",
    "role": "user"
  }
}
```

### POST `/api/v1/auth/register`
**Registro de nuevo usuario**

**Request:**
```json
{
  "email": "nuevo@empresa.com",
  "password": "password123",
  "full_name": "Juan Pérez"
}
```

**Response 201:** Igual a login.

### POST `/api/v1/auth/refresh`
**Renovar access token con refresh token**

**Header:** `Authorization: Bearer <refresh_token>`

**Response 200:**
```json
{"access_token": "...", "token_type": "bearer", "expires_in": 900}
```

### GET `/api/v1/auth/me`
**Perfil usuario actual**

**Header:** `Authorization: Bearer <access_token>`

**Response 200:**
```json
{
  "id": "uuid",
  "email": "usuario@empresa.com",
  "full_name": "Juan Pérez",
  "role": "user",
  "is_active": true,
  "created_at": "2026-08-20T10:00:00Z"
}
```

---

## Sitios (Sites)

### GET `/api/v1/sites`
**Listar sitios del usuario autenticado**

**Query params:**
- `page` (int, default 1)
- `size` (int, default 20, max 100)
- `site_type` (string, opcional filtro)

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Almacén Central Miami",
      "address": "123 NW 25th St, Miami, FL",
      "lat": 25.7617,
      "lon": -80.1918,
      "site_type": "warehouse",
      "metadata": {"heat_threshold_c": 35.0},
      "created_at": "2026-08-15T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### POST `/api/v1/sites`
**Crear sitio**

**Request:**
```json
{
  "name": "Oficina Matriz Austin",
  "address": "500 Congress Ave, Austin, TX",
  "lat": 30.2672,
  "lon": -97.7431,
  "site_type": "office",
  "metadata": {
    "heat_threshold_c": 32.0,
    "hvac_zones": ["floor_1", "floor_2"],
    "operating_hours": {"start": "08:00", "end": "18:00"}
  }
}
```

**Response 201:** Site object creado.

### GET `/api/v1/sites/{site_id}`
**Detalle de sitio**

**Response 200:** Site object completo.

### PATCH `/api/v1/sites/{site_id}`
**Actualizar sitio (parcial)**

### DELETE `/api/v1/sites/{site_id}`
**Eliminar sitio** (soft: `is_active=false`)

---

## Temperatura (Temperature)

### GET `/api/v1/sites/{site_id}/temperature/latest`
**Última lectura de temperatura**

**Response 200:**
```json
{
  "site_id": "uuid",
  "temperature_c": 36.5,
  "humidity_pct": 65.0,
  "heat_index_c": 42.1,
  "apparent_temp_c": 40.2,
  "source": "fortyguard",
  "recorded_at": "2026-08-20T14:00:00Z"
}
```

### GET `/api/v1/sites/{site_id}/temperature/history`
**Historial con filtros**

**Query params:**
- `start` (ISO datetime, requerido)
- `end` (ISO datetime, default now)
- `interval` (string: `raw`, `1h`, `6h`, `1d` - agregación)
- `unit` (string: `c`, `f` - default `c`)

**Response 200:**
```json
{
  "site_id": "uuid",
  "interval": "1h",
  "unit": "c",
  "data": [
    {"timestamp": "2026-08-20T13:00:00Z", "temperature_c": 35.2, "humidity_pct": 62},
    {"timestamp": "2026-08-20T14:00:00Z", "temperature_c": 36.5, "humidity_pct": 65}
  ],
  "stats": {"min": 34.1, "max": 37.8, "avg": 35.9}
}
```

### GET `/api/v1/sites/{site_id}/temperature/forecast`
**Pronóstico 24-72h desde FortyGuard**

**Query params:**
- `hours` (int, default 48, max 72)
- `unit` (c/f)

**Response 200:**
```json
{
  "site_id": "uuid",
  "source": "fortyguard",
  "generated_at": "2026-08-20T12:00:00Z",
  "forecast": [
    {"timestamp": "2026-08-20T13:00:00Z", "temperature_c": 37.0, "humidity_pct": 60},
    {"timestamp": "2026-08-20T14:00:00Z", "temperature_c": 38.2, "humidity_pct": 58}
  ]
}
```

### GET `/api/v1/sites/{site_id}/temperature/stats`
**Estadísticas agregadas**

**Query params:** `start`, `end` (requeridos)

**Response 200:**
```json
{
  "site_id": "uuid",
  "period": {"start": "2026-08-13T00:00:00Z", "end": "2026-08-20T00:00:00Z"},
  "temperature_c": {"min": 28.5, "max": 41.2, "avg": 34.8, "p95": 39.1},
  "heat_index_c": {"min": 30.1, "max": 48.5, "avg": 38.2},
  "exceedance_hours": {"threshold_c": 35, "hours_above": 42, "total_hours": 168}
}
```

---

## Alertas (Alerts)

### GET `/api/v1/sites/{site_id}/alerts`
**Listar alertas con filtros**

**Query params:**
- `page`, `size` (paginación)
- `severity` (info|warning|critical)
- `alert_type` (heat_risk|energy_waste|worker_safety|anomaly)
- `acknowledged` (true|false)
- `start`, `end` (rango fechas)

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "site_id": "uuid",
      "alert_type": "heat_risk",
      "severity": "critical",
      "title": "Temperatura crítica en Almacén Central",
      "message": "Temperatura 41.2°C excede umbral 35°C. Riesgo inventario y trabajadores.",
      "metadata": {
        "temperature_c": 41.2,
        "threshold_c": 35.0,
        "recommended_action": "Activar ventilación emergencia, mover inventario sensible, notificar turno"
      },
      "acknowledged": false,
      "created_at": "2026-08-20T14:05:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### PATCH `/api/v1/alerts/{alert_id}/acknowledge`
**Marcar alerta como reconocida**

**Request:**
```json
{"acknowledged": true}
```

**Response 200:** Alert object actualizado con `acknowledged_by`, `acknowledged_at`.

### GET `/api/v1/alerts/summary`
**Resumen alertas para dashboard (todos los sitios del usuario)**

**Response 200:**
```json
{
  "by_severity": {"critical": 2, "warning": 5, "info": 3},
  "by_type": {"heat_risk": 4, "energy_waste": 3, "worker_safety": 2, "anomaly": 1},
  "unacknowledged_count": 7,
  "latest_critical": {"id": "uuid", "title": "...", "created_at": "..."}
}
```

---

## Energía (Energy)

### GET `/api/v1/sites/{site_id}/energy/consumption`
**Historial consumo energético**

**Query params:** `start`, `end`, `zone_id` (opcional), `interval` (raw|1h|1d)

**Response 200:**
```json
{
  "site_id": "uuid",
  "interval": "1d",
  "data": [
    {"date": "2026-08-13", "kwh": 1250.5, "cost_usd": 187.58},
    {"date": "2026-08-14", "kwh": 1340.2, "cost_usd": 201.03}
  ],
  "totals": {"kwh": 9450.3, "cost_usd": 1417.55}
}
```

### GET `/api/v1/sites/{site_id}/energy/waste-analysis`
**Análisis desperdicio energético (AI)**

**Query params:** `days` (int, default 7)

**Response 200:**
```json
{
  "site_id": "uuid",
  "analysis_period_days": 7,
  "findings": [
    {
      "zone_id": "floor_1_zone_a",
      "issue": "overcooling",
      "description": "Zona mantenida a 19°C con exterior 15°C. Setpoint recomendado 22°C.",
      "estimated_waste_kwh_day": 45.2,
      "estimated_savings_usd_month": 180.5,
      "confidence": 0.87
    }
  ],
  "summary": {
    "total_waste_kwh": 316.4,
    "potential_monthly_savings_usd": 1265.0,
    "top_recommendation": "Subir setpoint zonas no críticas 2-3°C en horas no laborables"
  }
}
```

### POST `/api/v1/sites/{site_id}/energy/consumption`
**Ingesta manual datos energía (IoT, facturas, BMS)**

**Request:**
```json
{
  "zone_id": "datacenter_rack_3",
  "kwh": 245.5,
  "cost_usd": 36.83,
  "recorded_at": "2026-08-20T00:00:00Z",
  "metadata": {"equipment_type": "CRAC", "hvac_mode": "cooling"}
}
```

---

## Agente IA (Agent)

### POST `/api/v1/agent/chat`
**Consulta en lenguaje natural al agente**

**Request:**
```json
{
  "message": "¿Por qué el almacén de Miami gastó 20% más energía la semana pasada?",
  "site_id": "uuid",  // opcional, contexto
  "session_id": "uuid" // opcional, continuidad conversación
}
```

**Response 200:**
```json
{
  "session_id": "uuid",
  "response": {
    "reasoning": "Analicé consumo energético vs temperatura externa. Del 13-19 ago, Miami tuvo 5 días >38°C vs promedio 32°C. HVAC trabajó 40% más horas.",
    "actions_taken": [
      {"tool": "analyze_energy_waste", "site_id": "uuid", "result": "overcooling detected in zone_a"},
      {"tool": "query_knowledge_base", "query": "HVAC optimization hot climate", "result": "ASHRAE recommends..."}
    ],
    "recommendations": [
      "Subir setpoint zona_a de 20°C a 23°C en horas no laborables",
      "Programar mantenimiento preventivo coils condensador",
      "Evaluar aislamiento techo - ROI estimado 8 meses"
    ],
    "data_references": {
      "energy_analysis_id": "uuid",
      "temperature_correlation": 0.89
    }
  },
  "metadata": {
    "tools_used": ["analyze_energy_waste", "query_knowledge_base", "get_temperature_history"],
    "execution_time_ms": 2340,
    "tokens_used": 1450
  }
}
```

### POST `/api/v1/agent/execute`
**Ejecutar acción específica (manual override)**

**Request:**
```json
{
  "action": "create_alert",
  "params": {
    "site_id": "uuid",
    "alert_type": "worker_safety",
    "severity": "warning",
    "title": "Revisión manual turno noche",
    "message": "Supervisor solicita verificación condiciones turno 22:00-06:00"
  }
}
```

**Response 200:**
```json
{
  "action_id": "uuid",
  "status": "success",
  "result": {"alert_id": "uuid", "notification_sent": true},
  "execution_time_ms": 150
}
```

### GET `/api/v1/agent/status`
**Estado del agente**

**Response 200:**
```json
{
  "status": "healthy",
  "last_scheduled_run": "2026-08-20T14:00:00Z",
  "last_user_query": "2026-08-20T13:45:00Z",
  "tools_available": 7,
  "governance": {"policy": "omnitherm-agent", "calls_today": 42, "denied": 0},
  "trust_score": 0.92
}
```

---

## Esquemas Pydantic (Referencia)

```python
# app/schemas/temperature.py
class TemperatureReading(BaseModel):
    site_id: UUID
    temperature_c: float = Field(..., ge=-50, le=80)
    humidity_pct: Optional[float] = Field(None, ge=0, le=100)
    heat_index_c: Optional[float] = None
    apparent_temp_c: Optional[float] = None
    source: str = "fortyguard"
    recorded_at: datetime

class TemperatureForecast(BaseModel):
    timestamp: datetime
    temperature_c: float
    humidity_pct: Optional[float] = None
    heat_index_c: Optional[float] = None

class TemperatureStats(BaseModel):
    min: float
    max: float
    avg: float
    p95: Optional[float] = None

# app/schemas/alert.py
class AlertCreate(BaseModel):
    site_id: UUID
    alert_type: Literal["heat_risk", "energy_waste", "worker_safety", "anomaly"]
    severity: Literal["info", "warning", "critical"]
    title: str = Field(..., min_length=1, max_length=255)
    message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class AlertResponse(AlertCreate):
    id: UUID
    acknowledged: bool
    acknowledged_by: Optional[UUID]
    acknowledged_at: Optional[datetime]
    created_at: datetime

# app/schemas/agent.py
class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    site_id: Optional[UUID] = None
    session_id: Optional[UUID] = None

class AgentActionRequest(BaseModel):
    action: str
    params: Dict[str, Any] = {}
```