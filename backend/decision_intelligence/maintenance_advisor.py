from typing import Dict, Any, List
from datetime import datetime, timezone
from backend.telemetry.models import TelemetryData

class MaintenanceAdvisor:
    """
    Translates AI predictions, physics residuals, and digital twin states
    into specific aerospace maintenance tasks, alerts, and priority rankings.
    """

    @classmethod
    def generate_maintenance_advisories(
        cls,
        telem: TelemetryData,
        residuals: Dict[str, float],
        anomaly_data: Dict[str, Any],
        fault_data: Dict[str, Any],
        rul_data: Dict[str, Any],
        health_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        alerts = []
        recommendations = []
        urgent_actions = []

        health_score = health_data.get("health_score", 95.0)
        fault = fault_data.get("predicted_fault", "Nominal Operation")
        confidence = fault_data.get("confidence_pct", 95.0)
        hours_rem = rul_data.get("hours_remaining", 1000.0)

        # 1. Thermal Alerts & Recommendations
        if telem.cht > 230.0:
            alerts.append({
                "id": "ALT-TH-01",
                "severity": "CRITICAL",
                "system": "Cooling System",
                "message": f"Cylinder Head Temperature redline excursion: {telem.cht}°C (Residual: +{residuals.get('cht_residual')}°C)",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            urgent_actions.append("Reduce throttle to cruise loiter immediately; pitch down to increase cooling airspeed.")
            recommendations.append({
                "code": "TSK-COOL-401",
                "title": "Radiator & Coolant Jacket Overhaul",
                "priority": "P1 - Critical",
                "estimated_hours": 3.5,
                "procedure": "Pressure test cooling system at 1.2 bar. Flush radiator core, replace coolant expansion tank cap, and inspect cooling duct seals."
            })
        elif telem.cht > 195.0:
            alerts.append({
                "id": "ALT-TH-02",
                "severity": "WARNING",
                "system": "Cooling System",
                "message": f"Elevated CHT trend detected ({telem.cht}°C). Cooling reserve margin is depleted.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            recommendations.append({
                "code": "TSK-COOL-202",
                "title": "Cooling Baffle Inspection",
                "priority": "P2 - Medium",
                "estimated_hours": 1.0,
                "procedure": "Inspect cylinder silicone baffle seals for detachment or heat distortion."
            })

        # 2. Lubrication Alerts & Recommendations
        if telem.oil_press < 28.0:
            alerts.append({
                "id": "ALT-LUB-01",
                "severity": "CRITICAL",
                "system": "Lubrication Circuit",
                "message": f"Critical low oil pressure: {telem.oil_press} PSI (Threshold: 30 PSI min)",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            urgent_actions.append("Declare flight emergency. Execute engine-out / minimum power landing checklist.")
            recommendations.append({
                "code": "TSK-LUB-501",
                "title": "Scavenge Pump & Oil Filter Teardown",
                "priority": "P1 - Critical",
                "estimated_hours": 4.0,
                "procedure": "Cut open oil filter canister for spectrographic wear metal analysis; inspect pressure relief valve spring."
            })
        elif telem.oil_temp > 125.0:
            alerts.append({
                "id": "ALT-LUB-02",
                "severity": "WARNING",
                "system": "Lubrication Circuit",
                "message": f"High oil temperature ({telem.oil_temp}°C). Viscosity breakdown risk.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            recommendations.append({
                "code": "TSK-LUB-302",
                "title": "Oil Cooler Duct Flush & Oil Change",
                "priority": "P2 - Medium",
                "estimated_hours": 1.5,
                "procedure": "Drain aero-engine oil; replace with fresh AeroShell Oil Sport Plus 4; blow compressed air through oil cooler matrix."
            })

        # 3. Fuel & Injection Alerts
        if fault == "Injector Fault":
            alerts.append({
                "id": "ALT-FUEL-01",
                "severity": "WARNING",
                "system": "Fuel Injection Rail",
                "message": f"Injector flow unbalance detected with {confidence}% confidence.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            recommendations.append({
                "code": "TSK-INJ-310",
                "title": "Ultrasonic Injector Cleaning & Balance",
                "priority": "P2 - High",
                "estimated_hours": 2.0,
                "procedure": "Remove 4 fuel injectors. Clean ultrasonically in solvent bath and test flow rate on injector test bench."
            })

        # 4. RUL TBO Countdown
        if hours_rem < 200.0:
            recommendations.append({
                "code": "TSK-DEPOT-900",
                "title": "Depot-Level Scheduled Engine Overhaul",
                "priority": "P2 - Scheduled",
                "estimated_hours": 32.0,
                "procedure": f"Engine has reached {round(rul_data.get('accumulated_hours', 1000), 1)} equivalent operating hours. Schedule depot removal."
            })

        # Default nominal state
        if not alerts:
            alerts.append({
                "id": "ALT-SYS-OK",
                "severity": "INFO",
                "system": "All Subsystems",
                "message": "All propulsion parameters within standard flight envelope tolerances.",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            recommendations.append({
                "code": "TSK-ROUTINE-01",
                "title": "Routine 50-Hour Turnaround Inspection",
                "priority": "P3 - Routine",
                "estimated_hours": 0.5,
                "procedure": "Inspect oil sight glass, verify spark plug leads, check exhaust spring retention safety wires."
            })

        return {
            "active_alerts": alerts,
            "maintenance_recommendations": recommendations,
            "urgent_pilot_actions": urgent_actions,
            "total_pending_actions": len(recommendations)
        }
