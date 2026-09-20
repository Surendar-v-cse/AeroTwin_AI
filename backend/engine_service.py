import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Set
from fastapi import WebSocket

from backend.config import settings
from backend.database import (
    log_telemetry_record, log_twin_record, log_residuals_record,
    log_ai_record, get_recent_telemetry, get_recent_residuals
)
from backend.telemetry.models import TelemetryData, TelemetryUpdate, FaultInjection, MissionPhase
from backend.telemetry.simulator import SimulatorTelemetryProvider
from backend.digital_twin.twin_core import DigitalTwinEngine
from backend.ai_analytics.anomaly_detector import AnomalyDetectionEngine
from backend.ai_analytics.fault_classifier import FaultClassificationEngine
from backend.ai_analytics.trend_analyzer import TrendAnalysisEngine
from backend.ai_analytics.rul_engine import RemainingUsefulLifeEngine
from backend.ai_analytics.virtual_sensors import VirtualSensorEngine
from backend.ai_analytics.openai_advisor import OpenAIPropulsionAdvisor
from backend.decision_intelligence.health_scorer import HealthScoringEngine
from backend.decision_intelligence.readiness_engine import MissionReadinessEngine
from backend.decision_intelligence.maintenance_advisor import MaintenanceAdvisor

class EngineServiceOrchestrator:
    """
    Central Coordinator bridging Layer 1 to Layer 6:
      Layer 1: Telemetry Simulation
      Layer 2: Digital Twin Core
      Layer 3: Physics Engine
      Layer 4: AI Analytics
      Layer 5: Decision Intelligence
      Layer 6: Real-time C2 WebSocket Dispatch
    """

    def __init__(self):
        # Layer 1
        self.telemetry_provider = SimulatorTelemetryProvider()

        # Layer 2 & 3
        self.twin = DigitalTwinEngine(history_buffer_size=120)

        # Layer 4
        self.anomaly_detector = AnomalyDetectionEngine()
        self.fault_classifier = FaultClassificationEngine()
        self.trend_analyzer = TrendAnalysisEngine(window_size=60)
        self.rul_engine = RemainingUsefulLifeEngine()
        self.virtual_sensor_engine = VirtualSensorEngine()

        # Cache for latest complete payload
        self.latest_full_state: Optional[Dict[str, Any]] = None

        # Connected WebSocket clients
        self.active_websockets: Set[WebSocket] = set()

        # Background task
        self.running = False
        self.log_counter = 0

    def compute_all(self, telem: TelemetryData) -> Dict[str, Any]:
        # 1. Synchronize Digital Twin (includes physics evaluation & residuals)
        twin_state = self.twin.synchronize(telem)
        residuals = twin_state["residuals"]
        expected = twin_state["expected_state"]
        subsystems = twin_state["subsystems"]

        # 2. AI Anomaly Detection (Isolation Forest)
        anomaly_res = self.anomaly_detector.analyze(telem, residuals)

        # 3. AI Fault Classification (XGBoost / Random Forest)
        fault_res = self.fault_classifier.classify(telem, residuals)

        # 4. Decision Intelligence: Health Scoring
        health_res = HealthScoringEngine.calculate_health(
            telem=telem,
            residuals=residuals,
            anomaly_score=anomaly_res["anomaly_score"],
            fault_type=fault_res["predicted_fault"],
            fault_confidence=fault_res["confidence_pct"]
        )

        # 5. Trend Analysis
        trend_res = self.trend_analyzer.update(telem, health_res["health_score"])

        # 6. RUL Estimation
        rul_res = self.rul_engine.estimate_rul(
            telem=telem,
            residuals=residuals,
            anomaly_score=anomaly_res["anomaly_score"],
            fault_type=fault_res["predicted_fault"]
        )

        # 7. Virtual Sensors
        virtual_sensors = self.virtual_sensor_engine.synthesize_virtual_sensors(
            telem=telem,
            expected=expected,
            residuals=residuals,
            subsystems=subsystems,
            anomaly_score=anomaly_res["anomaly_score"]
        )

        # 8. Mission Readiness
        readiness_res = MissionReadinessEngine.evaluate_readiness(
            health_score=health_res["health_score"],
            anomaly_status=anomaly_res["anomaly_status"],
            predicted_fault=fault_res["predicted_fault"],
            is_critical_fault=fault_res["is_critical"]
        )

        # 9. Maintenance Advisories
        maint_res = MaintenanceAdvisor.generate_maintenance_advisories(
            telem=telem,
            residuals=residuals,
            anomaly_data=anomaly_res,
            fault_data=fault_res,
            rul_data=rul_res,
            health_data=health_res
        )

        full_payload = {
            "timestamp": telem.timestamp,
            "telemetry": telem.model_dump(),
            "simulation_mode": self.telemetry_provider.mode,
            "active_fault": self.telemetry_provider.active_fault,
            "expected_state": expected,
            "residuals": residuals,
            "residual_magnitude": twin_state["residual_magnitude"],
            "subsystems": subsystems,
            "predicted_state": twin_state["predicted_state"],
            "anomaly": anomaly_res,
            "faults": fault_res,
            "trends": trend_res,
            "rul": rul_res,
            "virtual_sensors": virtual_sensors,
            "health": health_res,
            "readiness": readiness_res,
            "maintenance": maint_res
        }

        self.latest_full_state = full_payload
        return full_payload

    async def run_simulation_loop(self):
        """Continuous async simulation tick loop (~2 Hz)."""
        self.running = True
        tick_interval = 1.0 / settings.simulation_tick_hz

        while self.running:
            try:
                # Step telemetry provider
                telem = self.telemetry_provider.step(dt=tick_interval)

                # Compute full 6-layer state
                payload = self.compute_all(telem)

                # Periodic database logging (e.g. every 5 ticks = every 2.5s)
                self.log_counter += 1
                if self.log_counter % 5 == 0:
                    log_telemetry_record(payload["telemetry"])
                    log_residuals_record(payload["residuals"])
                    log_ai_record({
                        "anomaly_score": payload["anomaly"]["anomaly_score"],
                        "anomaly_status": payload["anomaly"]["anomaly_status"],
                        "predicted_fault": payload["faults"]["predicted_fault"],
                        "fault_confidence": payload["faults"]["confidence_pct"],
                        "rul_hours": payload["rul"]["hours_remaining"],
                        "failure_prob": payload["rul"]["failure_probability_50h_pct"]
                    })

                # Broadcast to connected WebSockets
                await self.broadcast(payload)
            except Exception as e:
                print(f"[Engine Service Loop Error]: {e}")

            await asyncio.sleep(tick_interval)

    async def broadcast(self, payload: Dict[str, Any]):
        if not self.active_websockets:
            return

        disconnected = set()
        for ws in self.active_websockets:
            try:
                await ws.send_json(payload)
            except Exception:
                disconnected.add(ws)

        for dead_ws in disconnected:
            self.active_websockets.discard(dead_ws)

    def apply_scenario(self, scenario: str) -> Dict[str, Any]:
        """Applies pre-defined mission scenarios."""
        provider = self.telemetry_provider
        provider.set_mode("auto")

        if scenario == "high_altitude":
            provider.update_telemetry(TelemetryUpdate(
                altitude=22000.0,
                ambient_temp=-22.0,
                throttle=85.0,
                mission_phase=MissionPhase.CRUISE.value
            ))
            provider.inject_fault(FaultInjection(fault_type="none", severity=0.0))
            msg = "High Altitude Mission Profile Activated: 22,000 ft, cold thin atmosphere, turbo boost stress."

        elif scenario == "hot_weather":
            provider.update_telemetry(TelemetryUpdate(
                altitude=3500.0,
                ambient_temp=48.0,
                humidity=25.0,
                throttle=78.0,
                mission_phase=MissionPhase.LOITER.value
            ))
            provider.inject_fault(FaultInjection(fault_type="none", severity=0.0))
            msg = "Hot Weather Mission Profile Activated: 48°C ambient, cooling performance test."

        elif scenario == "endurance":
            provider.update_telemetry(TelemetryUpdate(
                altitude=15000.0,
                ambient_temp=-10.0,
                throttle=58.0,
                mission_phase=MissionPhase.LOITER.value
            ))
            provider.inject_fault(FaultInjection(fault_type="none", severity=0.0))
            msg = "Endurance Mission Profile Activated: Optimal cruise-loiter RPM and steady thermal envelope."

        elif scenario == "emergency":
            provider.update_telemetry(TelemetryUpdate(
                altitude=12000.0,
                ambient_temp=20.0,
                throttle=88.0,
                mission_phase=MissionPhase.CLIMB.value
            ))
            provider.inject_fault(FaultInjection(fault_type="cooling_duct_blockage", severity=0.9))
            msg = "Emergency Scenario Injected: Sudden radiator duct blockage & CHT thermal runaway."

        elif scenario == "nominal":
            provider.update_telemetry(TelemetryUpdate(
                altitude=12000.0,
                ambient_temp=12.0,
                humidity=45.0,
                throttle=70.0,
                mission_phase=MissionPhase.CRUISE.value
            ))
            provider.inject_fault(FaultInjection(fault_type="none", severity=0.0))
            msg = "Nominal Flight Profile Restored: All parameters reset to cruise baseline."
        else:
            msg = f"Unknown scenario '{scenario}'."

        telem = provider.get_current_telemetry()
        return {
            "scenario": scenario,
            "message": msg,
            "telemetry": telem.model_dump()
        }

engine_service = EngineServiceOrchestrator()
