from typing import Dict, Any
from backend.telemetry.models import TelemetryData

class VirtualSensorEngine:
    """
    Virtual Sensor Engine.
    Synthesizes unmeasured physical quantities from telemetry, physics residuals,
    and subsystem state estimations:
    - Engine Thermal Efficiency (%)
    - Cylinder Thermal Stress (0-100)
    - Piston & Bearing Wear Index (0-100)
    - Combustion Quality Score (0-100)
    - Overall Digital Twin Health Index (0-100)
    """

    @classmethod
    def synthesize_virtual_sensors(
        cls,
        telem: TelemetryData,
        expected: Dict[str, float],
        residuals: Dict[str, float],
        subsystems: Dict[str, Any],
        anomaly_score: float
    ) -> Dict[str, Any]:
        # 1. Engine Efficiency (%)
        eff = expected.get("expected_efficiency", 30.0) + residuals.get("efficiency_residual", 0.0)
        eff = max(10.0, min(42.0, eff))

        # 2. Cylinder Thermal Stress (0 - 100)
        thermal_state = subsystems.get("thermal_state", {})
        thermal_stress = thermal_state.get("thermal_stress_index", 45.0)

        # 3. Combustion Quality Score (0 - 100)
        combustion_state = subsystems.get("combustion_state", {})
        comb_quality = combustion_state.get("combustion_quality_score", 88.0)

        # 4. Wear Index (0 - 100)
        # Driven by high RPM, thermal cycles, and degraded oil film
        lubrication_state = subsystems.get("lubrication_state", {})
        film_integrity = lubrication_state.get("oil_film_integrity", 80.0)
        wear_index = min(100.0, max(5.0, (
            (telem.rpm / 6500.0) * 35.0 +
            (thermal_stress / 100.0) * 35.0 +
            (100.0 - film_integrity) * 0.30
        )))

        # 5. Overall Digital Twin Health Index (0 - 100)
        # Holistic composite synthesis
        health_raw = (
            comb_quality * 0.25 +
            (100.0 - thermal_stress) * 0.25 +
            (100.0 - wear_index) * 0.20 +
            (100.0 - anomaly_score * 100.0) * 0.30
        )
        health_index = max(5.0, min(100.0, health_raw))

        return {
            "engine_efficiency_pct": round(eff, 1),
            "cylinder_thermal_stress_index": round(thermal_stress, 1),
            "wear_index": round(wear_index, 1),
            "combustion_quality_score": round(comb_quality, 1),
            "overall_health_index": round(health_index, 1),
            "virtual_sensor_status": "Calibrated & Online"
        }
