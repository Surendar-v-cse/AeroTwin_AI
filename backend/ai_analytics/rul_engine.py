import math
from typing import Dict, Any
from backend.telemetry.models import TelemetryData

class RemainingUsefulLifeEngine:
    """
    Physics-Informed Remaining Useful Life (RUL) and Degradation Engine.
    Combines cumulative Miner's rule damage accumulation with Arrhenius thermal
    acceleration to predict flight hours remaining and 50-hour failure probability.
    """

    NOMINAL_TBO_HOURS = 1200.0   # Factory Time Between Overhauls
    BASE_HOURS_OPERATED = 340.0   # Current fleet engine accumulated hours

    @classmethod
    def estimate_rul(
        cls,
        telem: TelemetryData,
        residuals: Dict[str, float],
        anomaly_score: float,
        fault_type: str
    ) -> Dict[str, Any]:
        """
        Calculates remaining hours, health %, failure probability %,
        and an explainable breakdown of degradation contributors.
        """
        # 1. Thermal Fatigue Acceleration Factor (Arrhenius)
        # Reference CHT is 140°C (413.15 K). If CHT rises, damage accelerates exponentially.
        t_ref_k = 140.0 + 273.15
        t_cht_k = max(273.15 + 40.0, telem.cht + 273.15)
        # Activation energy proxy for aerospace aluminum cylinder head alloy
        thermal_accel = math.exp(2800.0 * (1.0 / t_ref_k - 1.0 / t_cht_k))
        thermal_accel = max(0.5, min(12.0, thermal_accel))

        # 2. Mechanical Load Acceleration Factor
        # Stress exponent ~ 2.5 for crankshaft and connecting rod fatigue
        rpm_ratio = telem.rpm / 5200.0
        mech_accel = math.pow(max(0.4, rpm_ratio), 2.5) * (telem.throttle / 70.0)
        mech_accel = max(0.4, min(8.0, mech_accel))

        # 3. Lubrication Degradation Penalty
        if telem.oil_press < 30.0 or telem.oil_temp > 125.0:
            oil_penalty = 3.5
        elif telem.oil_press < 45.0 or telem.oil_temp > 110.0:
            oil_penalty = 1.8
        else:
            oil_penalty = 1.0

        # 4. Physics Residual & Anomaly Degradation Multiplier
        residual_mag = (abs(residuals.get("cht_residual", 0.0)) / 10.0 +
                        abs(residuals.get("egt_residual", 0.0)) / 20.0 +
                        abs(residuals.get("oil_p_residual", 0.0)) / 5.0) / 3.0
        anomaly_penalty = 1.0 + anomaly_score * 2.0 + residual_mag * 0.5

        # 5. Composite Damage Acceleration Rate
        composite_wear_rate = thermal_accel * 0.35 + mech_accel * 0.25 + oil_penalty * 0.25 + anomaly_penalty * 0.15

        # If an active severe fault is detected, life drops steeply
        if fault_type in ("Cooling Failure", "Lubrication Issue", "Overheating"):
            composite_wear_rate *= 3.0
        elif fault_type in ("Injector Fault", "Combustion Instability"):
            composite_wear_rate *= 1.6

        # Effective equivalent operating hours consumed
        effective_hours_used = cls.BASE_HOURS_OPERATED * max(0.8, composite_wear_rate)
        remaining_hours = max(0.0, cls.NOMINAL_TBO_HOURS - effective_hours_used)

        # Health % (100% at 0 hours, down to 0% at TBO)
        health_pct = max(0.0, min(100.0, (remaining_hours / cls.NOMINAL_TBO_HOURS) * 100.0))

        # In-flight failure probability in the next 50 mission hours (Weibull hazard curve proxy)
        age_ratio = effective_hours_used / cls.NOMINAL_TBO_HOURS
        # Shape parameter beta ~ 2.8 (wear-out region)
        hazard = math.pow(age_ratio, 2.8) * (1.0 + anomaly_score * 3.0)
        failure_prob_pct = min(99.5, max(0.5, (1.0 - math.exp(-hazard * 0.15)) * 100.0))

        if fault_type in ("Cooling Failure", "Lubrication Issue") and anomaly_score > 0.7:
            failure_prob_pct = max(failure_prob_pct, 88.5)

        # Explainable degradation contributors (percentages summing to 100%)
        total_stress_units = (thermal_accel * 35.0 + mech_accel * 25.0 + oil_penalty * 25.0 + anomaly_penalty * 15.0)
        thermal_contrib = round((thermal_accel * 35.0 / total_stress_units) * 100.0, 1)
        mech_contrib = round((mech_accel * 25.0 / total_stress_units) * 100.0, 1)
        oil_contrib = round((oil_penalty * 25.0 / total_stress_units) * 100.0, 1)
        anomaly_contrib = round(100.0 - (thermal_contrib + mech_contrib + oil_contrib), 1)

        return {
            "hours_remaining": round(remaining_hours, 1),
            "nominal_tbo_hours": cls.NOMINAL_TBO_HOURS,
            "accumulated_hours": round(effective_hours_used, 1),
            "engine_health_pct": round(health_pct, 1),
            "failure_probability_50h_pct": round(failure_prob_pct, 1),
            "composite_wear_rate": round(composite_wear_rate, 2),
            "explainability": {
                "thermal_fatigue_contribution_pct": thermal_contrib,
                "mechanical_stress_contribution_pct": mech_contrib,
                "oil_degradation_contribution_pct": oil_contrib,
                "residual_anomaly_contribution_pct": anomaly_contrib
            }
        }
