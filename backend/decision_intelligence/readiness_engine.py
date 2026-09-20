from typing import Dict, Any

class MissionReadinessEngine:
    """
    Evaluates engine health against military UAV mission readiness criteria:
      - Ready: Health >= 88%, No critical faults, all thermal & oil margins nominal.
      - Ready with Monitoring: Health between 75% and 87%, slight residual drift.
      - Maintenance Recommended: Health between 60% and 74%, non-critical anomaly active.
      - Not Mission Ready: Health < 60%, active critical fault (lubrication, cooling runaway).
    """

    @classmethod
    def evaluate_readiness(
        cls,
        health_score: float,
        anomaly_status: str,
        predicted_fault: str,
        is_critical_fault: bool
    ) -> Dict[str, Any]:
        if health_score < 60.0 or is_critical_fault or anomaly_status == "Critical":
            readiness = "Not Mission Ready"
            badge_color = "red"
            description = "Engine violates airworthiness safety thresholds. Flight abort / grounding mandated."
            can_fly = False
        elif health_score < 75.0 or anomaly_status == "Warning" or predicted_fault != "Nominal Operation":
            readiness = "Maintenance Recommended"
            badge_color = "amber"
            description = "Pre-flight maintenance check or borescopic inspection required prior to dispatch."
            can_fly = False
        elif health_score < 88.0:
            readiness = "Ready with Monitoring"
            badge_color = "cyan"
            description = "Approved for mission sorties with enhanced GCS telemetry monitoring."
            can_fly = True
        else:
            readiness = "Ready"
            badge_color = "emerald"
            description = "Full mission clearance. Propulsion system operating in peak green band."
            can_fly = True

        return {
            "mission_readiness": readiness,
            "badge_color": badge_color,
            "description": description,
            "flight_authorized": can_fly
        }
