from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from app.agents.prompts import OMNITHERM_SYSTEM_PROMPT
from app.agents.governance import governed_tool, AGENT_POLICY, audit_trail
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

# Envolvemos las funciones usando nuestro decorador de gobernanza personalizado
tools = [
    governed_tool(get_current_temperature, AGENT_POLICY, audit_trail),
    governed_tool(get_temperature_forecast, AGENT_POLICY, audit_trail),
    governed_tool(query_site_data, AGENT_POLICY, audit_trail),
    governed_tool(create_alert, AGENT_POLICY, audit_trail),
    governed_tool(send_notification, AGENT_POLICY, audit_trail),
    governed_tool(analyze_energy_waste, AGENT_POLICY, audit_trail),
    governed_tool(query_knowledge_base, AGENT_POLICY, audit_trail),
    governed_tool(adjust_hvac_setpoint, AGENT_POLICY, audit_trail),  # Requiere revisión/aprobación
]

# Configuración del agente principal usando Gemini 2.0 Flash
omnitherm_agent = Agent(
    name="omnitherm_agent",
    model="gemini-2.0-flash",
    instruction=OMNITHERM_SYSTEM_PROMPT,
    tools=tools,
)

# Inicializamos el servicio de sesión en memoria y el Runner ejecutor
session_service = InMemorySessionService()

runner = Runner(
    agent=omnitherm_agent,
    app_name="omnitherm",
    session_service=session_service,
)

def get_agent_runner() -> Runner:
    """Función Singleton para obtener la instancia global del Runner."""
    return runner