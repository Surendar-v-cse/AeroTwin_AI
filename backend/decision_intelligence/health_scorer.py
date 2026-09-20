from typing import Dict, Any
from backend.telemetry.models import TelemetryData

class HealthScoringEngine:
    """
    Computes a composite Propulsion Health Score (0 - 100).
    Categories:
      90 - 100: Excellent (Nominal flight operations)
      75 - 89:  Good (Acceptable performance, standard monitoring)
      60 - 74:  Warning (Elevated thermal or mechanical stress)
      Below 60: Critical (Immediate pilot/GCS intervention required)
    """

    @classmethod
    def calculate_health(
        cls,
        telem: TelemetryData,
        residuals: Dict[str, float],
        anomaly_score: float,
        fault_type: str,
        fault_confidence: float
    ) -> Dict[str, Any]:
        # Start from base 100
        score = 100.0

        # Penalty 1: Direct Anomaly Score penalty (up to -35 points)
        score -= anomaly_score * 35.0

        # Penalty 2: Physics Residual deviation penalty
        cht_res_penalty = min(25.0, abs(residuals.get("cht_residual", 0.0)) * 0.4)
        egt_res_penalty = min(15.0, abs(residuals.get("egt_residual", 0.0)) * 0.15)
        oil_res_penalty = min(25.0, abs(residuals.get("oil_p_residual", 0.0)) * 0.7)
        score -= (cht_res_penalty + egt_res_penalty + oil_res_penalty)

        # Penalty 3: Hard limit breaches
        if telem.cht > 240.0:
            score -= 30.0
        elif telem.cht > 205.0:
            score -= 15.0

        if telem.oil_press < 25.0:
            score -= 35.0
        elif telem.oil_press < 40.0:
            score -= 12.0

        if telem.oil_temp > 130.0:
            score -= 25.0
        elif telem.oil_temp > 115.0:
            score -= 10.0

        if telem.egt > 870.0:
            score -= 20.0

        # Penalty 4: Known Fault Classifier penalty
        if fault_type in ("Cooling Failure", "Lubrication Issue", "Overheating"):
            score -= (fault_confidence / 100.0) * 28.0
        elif fault_type in ("Injector Fault", "Combustion Instability"):
            score -= (fault_confidence / 100.0) * 16.0

        # Bound score between 0 and 100
        health_score = round(max(5.0, min(100.0, score)), 1)

        # Categorize
        if health_score >= 90.0:
            category = "Excellent"
            color = "emerald"
        elif health_score >= 75.0:
            category = "Good"
            color = "cyan"
        elif health_score >= 60.0:
            category = "Warning"
            color = "amber"
        else:
            category = "Critical"
            color = "rose"

        return {
            "health_score": health_score,
            "health_category": category,
            "status_color": color,
            "deductions": {
                "anomaly_deduction": round(anomaly_score * 35.0, 1),
                "physics_residual_deduction": round(cht_res_penalty + egt_res_penalty + oil_res_penalty, 1),
                "operational_limit_deduction": round(max(0.0, 100.0 - score - (anomaly_score * 35.0)), 1)
            }
        }
