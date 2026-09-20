from fastapi import APIRouter
from typing import Dict, Any
from backend.telemetry.models import MissionScenarioRequest
from backend.engine_service import engine_service

router = APIRouter(prefix="/api", tags=["Mission Simulation & Operations"])

@router.post("/simulation")
def trigger_mission_simulation(req: MissionScenarioRequest):
    """
    Simulate mission scenarios:
      - 'high_altitude': 22,000 ft climb, low temp, turbo boost stress
      - 'hot_weather': 48°C ambient, CHT thermal dissipation stress
      - 'endurance': 14-hr optimal loiter
      - 'emergency': sudden cooling failure / CHT thermal runaway
      - 'nominal': reset to standard cruise
    """
    return engine_service.apply_scenario(req.scenario)

@router.get("/maintenance")
def get_maintenance_advisories():
    """Retrieve active maintenance alerts and recommended ground/pilot actions."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return state["maintenance"]

@router.get("/mission-report")
def get_mission_report():
    """Generate a comprehensive mission summary report."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return {
        "aircraft_callsign": "AEROTWIN-UAV-01",
        "engine_type": "ROTAX 914 TURBOCHARGED AERO-PISTON",
        "timestamp": state["timestamp"],
        "mission_phase": state["telemetry"]["mission_phase"],
        "health_score": state["health"]["health_score"],
        "health_category": state["health"]["health_category"],
        "mission_readiness": state["readiness"]["mission_readiness"],
        "rul_hours_remaining": state["rul"]["hours_remaining"],
        "50h_failure_probability_pct": state["rul"]["failure_probability_50h_pct"],
        "anomaly_status": state["anomaly"]["anomaly_status"],
        "predicted_fault": state["faults"]["predicted_fault"],
        "fault_confidence_pct": state["faults"]["confidence_pct"],
        "engine_efficiency_pct": state["virtual_sensors"]["engine_efficiency_pct"],
        "cylinder_thermal_stress_index": state["virtual_sensors"]["cylinder_thermal_stress_index"],
        "active_maintenance_alerts": len(state["maintenance"]["active_alerts"]),
        "recommendations_count": len(state["maintenance"]["maintenance_recommendations"])
    }
