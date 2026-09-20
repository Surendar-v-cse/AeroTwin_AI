from fastapi import APIRouter
from typing import Dict, Any, List
from backend.engine_service import engine_service
from backend.database import get_recent_residuals

router = APIRouter(prefix="/api/twin", tags=["Digital Twin"])

@router.get("")
def get_digital_twin():
    """Retrieve full Digital Twin state (Current, Expected, Predicted, Subsystems)."""
    if engine_service.latest_full_state:
        return engine_service.latest_full_state
    telem = engine_service.telemetry_provider.get_current_telemetry()
    return engine_service.compute_all(telem)

@router.get("/residuals")
def get_residuals():
    """Get physics residuals (Actual - Expected) and deviation metrics."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return {
        "expected": state["expected_state"],
        "residuals": state["residuals"],
        "residual_magnitude": state["residual_magnitude"]
    }

@router.get("/residuals/history")
def get_residuals_history(limit: int = 60):
    """Get historical physics residuals for trend visualization."""
    return get_recent_residuals(limit=limit)

@router.get("/subsystems")
def get_subsystem_states():
    """Get estimated states for Thermal, Mechanical, Combustion, Lubrication, Fuel."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return state["subsystems"]
