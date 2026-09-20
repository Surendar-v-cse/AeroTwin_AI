from typing import Dict, Any
from backend.telemetry.models import TelemetryData
from backend.physics.engine_model import AeroPistonEnginePhysics

class PhysicsResidualEngine:
    """
    Computes residuals (Actual - Expected) between real-time telemetry
    and the first-principles physics model.
    """

    @classmethod
    def compute_residuals(cls, telem: TelemetryData) -> Dict[str, Any]:
        # 1. Compute physics-expected baseline
        expected = AeroPistonEnginePhysics.calculate_expected_states(
            throttle=telem.throttle,
            rpm=telem.rpm,
            altitude=telem.altitude,
            ambient_temp=telem.ambient_temp,
            humidity=telem.humidity
        )

        # 2. Derive actual thermal stress and efficiency proxies
        effective_ambient = telem.ambient_temp - (telem.altitude / 1000.0) * 1.98
        actual_delta_t = max(10.0, telem.cht - effective_ambient)
        actual_thermal_stress = min(100.0, (actual_delta_t / 200.0) * 80.0)

        # Estimated power from actual RPM & throttle
        rpm_ratio = max(0.2, min(1.2, telem.rpm / 5800.0))
        actual_power_hp = 115.0 * (telem.throttle / 100.0) * (0.3 + 0.7 * rpm_ratio)
        actual_power_kw = actual_power_hp * 0.7457
        actual_fuel_kg_h = max(0.5, telem.fuel_flow * 0.73)
        actual_fuel_kw = (actual_fuel_kg_h / 3600.0) * (43.5 * 1000.0)
        actual_efficiency = max(12.0, min(42.0, (actual_power_kw / actual_fuel_kw) * 100.0))

        # 3. Calculate Residuals (Actual - Expected)
        egt_residual = telem.egt - expected["expected_egt"]
        cht_residual = telem.cht - expected["expected_cht"]
        fuel_residual = telem.fuel_flow - expected["expected_fuel_flow"]
        oil_p_residual = telem.oil_press - expected["expected_oil_press"]
        oil_t_residual = telem.oil_temp - expected["expected_oil_temp"]
        thermal_stress_residual = actual_thermal_stress - expected["expected_thermal_stress"]
        efficiency_residual = actual_efficiency - expected["expected_efficiency"]

        return {
            "expected": expected,
            "actual_power_hp": round(actual_power_hp, 1),
            "actual_thermal_stress": round(actual_thermal_stress, 1),
            "actual_efficiency": round(actual_efficiency, 1),
            "residuals": {
                "egt_residual": round(egt_residual, 1),
                "cht_residual": round(cht_residual, 1),
                "fuel_residual": round(fuel_residual, 2),
                "oil_p_residual": round(oil_p_residual, 1),
                "oil_t_residual": round(oil_t_residual, 1),
                "thermal_stress_residual": round(thermal_stress_residual, 1),
                "efficiency_residual": round(efficiency_residual, 1),
            },
            # Normalized Euclidean residual distance (physics deviation magnitude)
            "residual_magnitude": round(
                (abs(egt_residual)/30.0 + abs(cht_residual)/15.0 + abs(fuel_residual)/3.0 + abs(oil_p_residual)/8.0) / 4.0,
                3
            )
        }
