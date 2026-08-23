from datetime import datetime, timedelta, timezone
from app.repositories import TemperatureRepository, EnergyRepository, AgentActionRepository, AlertRepository

# Adaptación dinámica
try:
    temp_repo = TemperatureRepository(None, None)
except TypeError:
    temp_repo = TemperatureRepository(None)

try:
    energy_repo = EnergyRepository(None, None)
except TypeError:
    energy_repo = EnergyRepository(None)

try:
    agent_action_repo = AgentActionRepository(None, None)
except TypeError:
    agent_action_repo = AgentActionRepository(None)

try:
    alert_repo = AlertRepository(None, None)
except TypeError:
    alert_repo = AlertRepository(None)

async def analyze_energy_waste(site_id: str, days: int = 7) -> dict:
    """Detecta overcooling comparando temp externa vs consumo HVAC."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    
    temps = await temp_repo.get_range(site_id, start, end)
    energy = await energy_repo.get_range(site_id, start, end)
    
    threshold = 50.0
    findings = []
    
    for zone, cons in energy.groupby("zone_id"):
        avg_ext_temp = temps["temperature_c"].mean() if not temps.empty else 25.0
        avg_consumption = cons["kwh"].mean()
        
        if avg_ext_temp < 18.0 and avg_consumption > threshold:
            findings.append({
                "zone_id": zone,
                "issue": "overcooling",
                "avg_external_temp_c": round(avg_ext_temp, 1),
                "avg_consumption_kwh": round(avg_consumption, 1),
                "recommended_setpoint_c": 22.0,
                "estimated_savings_usd_month": round((avg_consumption * 0.15) * 30 * 0.15, 2)
            })
            
    return {"site_id": site_id, "period_days": days, "findings": findings}

async def adjust_hvac_setpoint(site_id: str, zone_id: str, new_setpoint_c: float) -> dict:
    """Ajusta setpoint HVAC. REQUIERE APROBACIÓN HUMANA (governance policy)."""
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