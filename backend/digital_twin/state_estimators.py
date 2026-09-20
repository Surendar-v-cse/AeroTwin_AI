import math
from typing import Dict, Any
from backend.telemetry.models import TelemetryData

class SubsystemStateEstimators:
    """
    Computes virtual state representations for the 5 key aero-piston subsystems:
    Thermal, Mechanical, Combustion, Lubrication, and Fuel System.
    """

    @classmethod
    def estimate_thermal_state(cls, telem: TelemetryData, expected: Dict[str, float]) -> Dict[str, Any]:
        # Redlines for Rotax 914: Max CHT is 135°C (continuous) / 150°C (takeoff 5-min) / 175°C max limit
        cht_margin = max(0.0, 220.0 - telem.cht)
        egt_margin = max(0.0, 880.0 - telem.egt)

        # Thermal gradient between exhaust port and cylinder head
        thermal_gradient = max(0.0, telem.egt - telem.cht)

        # Estimated heat rejection rate to coolant/air (kW)
        heat_flux_kw = (telem.throttle / 100.0) * 38.0 + (telem.cht / 150.0) * 12.0

        # Thermal stress index (0 - 100)
        thermal_stress_idx = min(100.0, (telem.cht / 230.0) * 70.0 + (telem.oil_temp / 130.0) * 30.0)

        # Status categorization
        if telem.cht > 235 or telem.egt > 870:
            status = "Critical"
        elif telem.cht > 200 or telem.egt > 830:
            status = "Warning"
        else:
            status = "Nominal"

        return {
            "status": status,
            "cht_margin_c": round(cht_margin, 1),
            "egt_margin_c": round(egt_margin, 1),
            "thermal_gradient_c": round(thermal_gradient, 1),
            "heat_flux_kw": round(heat_flux_kw, 1),
            "thermal_stress_index": round(thermal_stress_idx, 1),
            "cooling_reserve_pct": round(min(100.0, (cht_margin / 120.0) * 100.0), 1)
        }

    @classmethod
    def estimate_mechanical_state(cls, telem: TelemetryData, expected: Dict[str, float]) -> Dict[str, Any]:
        # Estimated torque: Torque (Nm) = (Power (kW) * 9548.8) / RPM
        rpm = max(1000.0, telem.rpm)
        power_hp = expected.get("expected_power_hp", 85.0)
        power_kw = power_hp * 0.7457
        torque_nm = (power_kw * 9548.8) / rpm

        # Mechanical stress index (combination of RPM inertia load and gas cylinder pressure)
        rpm_factor = math.pow(rpm / 5800.0, 2)
        mech_stress_idx = min(100.0, (rpm_factor * 60.0 + (telem.throttle / 100.0) * 40.0))

        # Vibration risk proxy: resonance zones near 2200-2400 RPM or overspeed > 6200 RPM
        if rpm > 6400:
            vibration_risk = min(100.0, 50.0 + (rpm - 6400) / 10.0)
        elif 2200 <= rpm <= 2450:
            vibration_risk = 45.0  # Harmonic resonance band
        else:
            vibration_risk = max(10.0, (rpm / 6000.0) * 25.0)

        if mech_stress_idx > 88 or vibration_risk > 70:
            status = "Critical"
        elif mech_stress_idx > 75 or vibration_risk > 40:
            status = "Warning"
        else:
            status = "Nominal"

        return {
            "status": status,
            "power_output_hp": round(power_hp, 1),
            "torque_nm": round(torque_nm, 1),
            "mechanical_stress_index": round(mech_stress_idx, 1),
            "vibration_risk_index": round(vibration_risk, 1),
            "overspeed_margin_rpm": round(max(0.0, 6800.0 - rpm), 0)
        }

    @classmethod
    def estimate_combustion_state(cls, telem: TelemetryData, expected: Dict[str, float]) -> Dict[str, Any]:
        # Equivalence / Air-Fuel Stoichiometric Lambda proxy
        # Nominal lambda is 1.0 (stoichiometric 14.7:1), < 1.0 is rich, > 1.0 is lean
        # Estimate theoretical airflow from RPM, throttle, and air density
        sigma = expected.get("air_density_sigma", 1.0)
        est_air_flow_kg_h = (telem.rpm / 5800.0) * (telem.throttle / 100.0) * 180.0 * sigma
        est_fuel_kg_h = max(0.5, telem.fuel_flow * 0.73)
        actual_afr = est_air_flow_kg_h / est_fuel_kg_h
        lambda_val = actual_afr / 14.7
        lambda_val = max(0.70, min(1.40, lambda_val))

        # Combustion stability: optimal when lambda is between 0.90 and 1.08
        if 0.90 <= lambda_val <= 1.08:
            combustion_quality = 95.0 - abs(lambda_val - 1.0) * 50.0
            detonation_risk = 5.0
        elif lambda_val > 1.08:
            # Overly lean: detonation / knock risk increases, EGT high
            combustion_quality = max(20.0, 95.0 - (lambda_val - 1.08) * 200.0)
            detonation_risk = min(100.0, 20.0 + (lambda_val - 1.08) * 300.0)
        else:
            # Overly rich: unburnt HC, fouling risk, low efficiency
            combustion_quality = max(30.0, 95.0 - (0.90 - lambda_val) * 150.0)
            detonation_risk = 5.0

        if combustion_quality < 55 or detonation_risk > 60:
            status = "Critical"
        elif combustion_quality < 75 or detonation_risk > 30:
            status = "Warning"
        else:
            status = "Nominal"

        return {
            "status": status,
            "lambda_ratio": round(lambda_val, 2),
            "estimated_afr": round(actual_afr, 1),
            "combustion_quality_score": round(combustion_quality, 1),
            "detonation_risk_index": round(detonation_risk, 1),
            "misfire_risk_pct": round(max(0.0, 100.0 - combustion_quality), 1)
        }

    @classmethod
    def estimate_lubrication_state(cls, telem: TelemetryData, expected: Dict[str, float]) -> Dict[str, Any]:
        # Kinematic viscosity proxy (cSt) for SAE 15W-50 aero oil
        # Viscosity drops exponentially with temperature
        oil_t = max(20.0, min(160.0, telem.oil_temp))
        viscosity_cst = 140.0 * math.exp(-0.025 * (oil_t - 40.0))

        # Dynamic hydrodynamic oil film thickness index (0-100)
        # Sommerfeld number proxy: film ~ (viscosity * RPM) / bearing_load
        rpm_ratio = telem.rpm / 5000.0
        pressure_factor = telem.oil_press / 55.0
        oil_film_index = min(100.0, max(5.0, (viscosity_cst / 25.0) * rpm_ratio * pressure_factor * 50.0))

        # Lubrication degradation index: increases if oil temp has been above 115°C
        if oil_t > 120.0:
            degradation_rate = 75.0 + (oil_t - 120.0) * 1.5
        elif oil_t > 105.0:
            degradation_rate = 40.0 + (oil_t - 105.0) * 2.0
        else:
            degradation_rate = 15.0

        if telem.oil_press < 25.0 or oil_t > 135.0 or oil_film_index < 25.0:
            status = "Critical"
        elif telem.oil_press < 40.0 or oil_t > 115.0 or oil_film_index < 50.0:
            status = "Warning"
        else:
            status = "Nominal"

        return {
            "status": status,
            "viscosity_cst": round(viscosity_cst, 1),
            "oil_film_integrity": round(oil_film_index, 1),
            "lubrication_degradation_index": round(degradation_rate, 1),
            "scavenge_pressure_margin_psi": round(max(0.0, telem.oil_press - 20.0), 1)
        }

    @classmethod
    def estimate_fuel_system_state(cls, telem: TelemetryData, expected: Dict[str, float]) -> Dict[str, Any]:
        # Fuel delivery compliance
        exp_fuel = expected.get("expected_fuel_flow", 22.0)
        fuel_diff = telem.fuel_flow - exp_fuel
        fuel_delivery_margin = 100.0 - min(100.0, (abs(fuel_diff) / max(1.0, exp_fuel)) * 100.0)

        # Injector duty cycle proxy (0 - 100%)
        injector_duty = min(100.0, (telem.fuel_flow / 38.0) * 100.0)

        # Vapor lock risk (high fuel temp / high altitude / low atmospheric pressure)
        vapor_lock_risk = min(100.0, max(0.0, (telem.ambient_temp / 50.0) * 40.0 + (telem.altitude / 25000.0) * 60.0))

        if fuel_delivery_margin < 60.0 or injector_duty > 95.0 or vapor_lock_risk > 80.0:
            status = "Critical"
        elif fuel_delivery_margin < 80.0 or injector_duty > 85.0 or vapor_lock_risk > 50.0:
            status = "Warning"
        else:
            status = "Nominal"

        return {
            "status": status,
            "injector_duty_cycle_pct": round(injector_duty, 1),
            "delivery_compliance_pct": round(fuel_delivery_margin, 1),
            "vapor_lock_risk_index": round(vapor_lock_risk, 1),
            "fuel_rail_pressure_margin": "Nominal" if telem.fuel_flow > 2.0 else "Low"
        }
