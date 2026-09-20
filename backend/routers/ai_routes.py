from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
from backend.engine_service import engine_service
from backend.ai_analytics.openai_advisor import OpenAIPropulsionAdvisor

router = APIRouter(prefix="/api", tags=["AI Analytics & Decision Intelligence"])

class AIInsightRequest(BaseModel):
    api_key: Optional[str] = None

@router.get("/anomaly")
def get_anomaly_status():
    """Retrieve Isolation Forest anomaly score and status (Normal/Warning/Critical)."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return state["anomaly"]

@router.get("/faults")
def get_fault_classification():
    """Retrieve predicted fault, confidence percentage, and multi-class distribution."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return state["faults"]

@router.get("/rul")
def get_rul():
    """Retrieve Remaining Useful Life (RUL) flight hours, health %, and failure risk."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return state["rul"]

@router.get("/health")
def get_health_score():
    """Retrieve composite Health Score (0-100) and Mission Readiness."""
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )
    return {
        "health": state["health"],
        "readiness": state["readiness"]
    }

@router.post("/ai-insights")
def generate_ai_insights(req: AIInsightRequest = AIInsightRequest()):
    """
    Generate AI Maintenance Report, Mission Risk Assessment, Root Cause Analysis,
    and Recommended Actions via OpenAI (or local Aerospace Expert Heuristic fallback).
    """
    state = engine_service.latest_full_state or engine_service.compute_all(
        engine_service.telemetry_provider.get_current_telemetry()
    )

    insights = OpenAIPropulsionAdvisor.generate_insights(
        telemetry=state["telemetry"],
        physics_residuals=state["residuals"],
        anomaly_data=state["anomaly"],
        fault_data=state["faults"],
        rul_data=state["rul"],
        health_score=state["health"]["health_score"],
        api_key_override=req.api_key
    )
    return insights
