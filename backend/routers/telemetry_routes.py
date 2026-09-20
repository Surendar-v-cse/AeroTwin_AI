from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.telemetry.models import TelemetryData, TelemetryUpdate, FaultInjection
from backend.engine_service import engine_service
from backend.database import get_recent_telemetry

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

@router.get("", response_model=TelemetryData)
def get_telemetry():
    """Retrieve current telemetry reading."""
    return engine_service.telemetry_provider.get_current_telemetry()

@router.post("", response_model=Dict[str, Any])
def update_telemetry(update: TelemetryUpdate):
    """Manually update telemetry variables or switch operating mode."""
    updated_telem = engine_service.telemetry_provider.update_telemetry(update)
    payload = engine_service.compute_all(updated_telem)
    return {
        "status": "success",
        "telemetry": updated_telem.model_dump(),
        "mode": engine_service.telemetry_provider.mode,
        "health_score": payload["health"]["health_score"]
    }

@router.post("/mode")
def set_simulator_mode(mode: str):
    """Switch between Mode A ('manual') and Mode B ('auto')."""
    if mode not in ("manual", "auto"):
        raise HTTPException(status_code=400, detail="Mode must be 'manual' or 'auto'")
    engine_service.telemetry_provider.set_mode(mode)
    return {"status": "success", "mode": mode}

@router.post("/inject-fault")
def inject_fault(fault: FaultInjection):
    """Inject a physical fault condition into the telemetry simulator."""
    engine_service.telemetry_provider.inject_fault(fault)
    return {
        "status": "success",
        "active_fault": fault.fault_type,
        "severity": fault.severity
    }

@router.get("/history")
def get_history(limit: int = 60):
    """Fetch recent historical telemetry samples for timeline visualization."""
    return get_recent_telemetry(limit=limit)
