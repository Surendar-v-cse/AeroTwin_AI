from collections import deque
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.telemetry.models import TelemetryData
from backend.physics.residual_engine import PhysicsResidualEngine
from backend.digital_twin.state_estimators import SubsystemStateEstimators

class DigitalTwinEngine:
    """
    Virtual Engine Digital Twin Core.
    Maintains a real-time synchronized virtual representation of the MALE UAV aero-piston engine,
    storing Current State, Historical Trajectory, Expected Physics Baseline, and Predicted Forward States.
    """

    def __init__(self, history_buffer_size: int = 120):
        self.history_buffer = deque(maxlen=history_buffer_size)
        self.current_state: Optional[Dict[str, Any]] = None
        self.expected_state: Optional[Dict[str, Any]] = None
        self.predicted_state: Optional[Dict[str, Any]] = None
        self.latest_residuals: Optional[Dict[str, Any]] = None
        self.subsystems: Optional[Dict[str, Any]] = None

    def synchronize(self, telem: TelemetryData) -> Dict[str, Any]:
        """
        Synchronize the digital twin with the latest incoming telemetry packet.
        Executes physics baseline evaluation, residual extraction, and subsystem state estimations.
        """
        # 1. Physics Engine Residual Evaluation
        physics_eval = PhysicsResidualEngine.compute_residuals(telem)
        self.expected_state = physics_eval["expected"]
        self.latest_residuals = physics_eval["residuals"]

        # 2. Subsystem State Estimations
        thermal = SubsystemStateEstimators.estimate_thermal_state(telem, self.expected_state)
        mechanical = SubsystemStateEstimators.estimate_mechanical_state(telem, self.expected_state)
        combustion = SubsystemStateEstimators.estimate_combustion_state(telem, self.expected_state)
        lubrication = SubsystemStateEstimators.estimate_lubrication_state(telem, self.expected_state)
        fuel_sys = SubsystemStateEstimators.estimate_fuel_system_state(telem, self.expected_state)

        self.subsystems = {
            "thermal_state": thermal,
            "mechanical_state": mechanical,
            "combustion_state": combustion,
            "lubrication_state": lubrication,
            "fuel_state": fuel_sys
        }

        # 3. Predicted Forward State (30 seconds lookahead based on derivative trend)
        predicted = self._extrapolate_forward_state(telem, dt_future_sec=30.0)
        self.predicted_state = predicted

        # 4. Assemble Current Digital Twin State
        full_twin_state = {
            "timestamp": telem.timestamp,
            "telemetry": telem.model_dump(),
            "expected_state": self.expected_state,
            "residuals": self.latest_residuals,
            "residual_magnitude": physics_eval["residual_magnitude"],
            "subsystems": self.subsystems,
            "predicted_state": self.predicted_state
        }

        self.current_state = full_twin_state
        self.history_buffer.append(full_twin_state)

        return full_twin_state

    def _extrapolate_forward_state(self, current_telem: TelemetryData, dt_future_sec: float = 30.0) -> Dict[str, Any]:
        """Extrapolates next 30-sec trajectory from historical rate-of-change."""
        if len(self.history_buffer) < 5:
            # Not enough history for derivative; project steady state
            return {
                "horizon_sec": dt_future_sec,
                "projected_cht": current_telem.cht,
                "projected_egt": current_telem.egt,
                "projected_oil_temp": current_telem.oil_temp,
                "projected_oil_press": current_telem.oil_press,
                "thermal_trajectory": "Stable"
            }

        prev_state = self.history_buffer[-5]["telemetry"]
        dt = 2.5  # approx time over 5 samples @ 2 Hz

        d_cht_dt = (current_telem.cht - prev_state["cht"]) / dt
        d_egt_dt = (current_telem.egt - prev_state["egt"]) / dt
        d_oil_t_dt = (current_telem.oil_temp - prev_state["oil_temp"]) / dt
        d_oil_p_dt = (current_telem.oil_press - prev_state["oil_press"]) / dt

        proj_cht = max(40.0, min(320.0, current_telem.cht + d_cht_dt * dt_future_sec))
        proj_egt = max(250.0, min(950.0, current_telem.egt + d_egt_dt * dt_future_sec))
        proj_oil_t = max(20.0, min(160.0, current_telem.oil_temp + d_oil_t_dt * dt_future_sec))
        proj_oil_p = max(5.0, min(120.0, current_telem.oil_press + d_oil_p_dt * dt_future_sec))

        if d_cht_dt > 0.8 or d_oil_t_dt > 0.5:
            trajectory = "Rapid Thermal Rise"
        elif d_cht_dt < -0.8:
            trajectory = "Rapid Cooling"
        else:
            trajectory = "Stable Cruise"

        return {
            "horizon_sec": dt_future_sec,
            "projected_cht": round(proj_cht, 1),
            "projected_egt": round(proj_egt, 1),
            "projected_oil_temp": round(proj_oil_t, 1),
            "projected_oil_press": round(proj_oil_p, 1),
            "cht_rate_c_per_sec": round(d_cht_dt, 2),
            "thermal_trajectory": trajectory
        }

    def get_history_summary(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.history_buffer)[-limit:]
