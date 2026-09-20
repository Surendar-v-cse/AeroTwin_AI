import json
from typing import Dict, Any, Optional
from openai import OpenAI
from backend.config import settings

class OpenAIPropulsionAdvisor:
    """
    OpenAI-Powered Propulsion Intelligence & Autonomous Maintenance Advisor.
    Takes full Digital Twin telemetry, anomalies, residuals, and physics states,
    and queries OpenAI (or executes a specialized Aerospace Propulsion Expert Heuristic Engine)
    to generate structured defense-grade reports.
    """

    @classmethod
    def generate_insights(
        cls,
        telemetry: Dict[str, Any],
        physics_residuals: Dict[str, Any],
        anomaly_data: Dict[str, Any],
        fault_data: Dict[str, Any],
        rul_data: Dict[str, Any],
        health_score: float,
        api_key_override: Optional[str] = None
    ) -> Dict[str, Any]:
        api_key = api_key_override or settings.openai_api_key

        if api_key and api_key.strip():
            try:
                return cls._query_openai(
                    api_key=api_key.strip(),
                    telemetry=telemetry,
                    physics_residuals=physics_residuals,
                    anomaly_data=anomaly_data,
                    fault_data=fault_data,
                    rul_data=rul_data,
                    health_score=health_score
                )
            except Exception as e:
                print(f"[OpenAI Propulsion Advisor] OpenAI API call failed: {e}. Falling back to Aerospace Expert Heuristic Engine.")
                fallback = cls._aerospace_expert_fallback(telemetry, physics_residuals, anomaly_data, fault_data, rul_data, health_score)
                fallback["llm_source"] = "Aerospace Propulsion Expert Engine (OpenAI API Error Fallback)"
                fallback["error_detail"] = str(e)
                return fallback
        else:
            fallback = cls._aerospace_expert_fallback(telemetry, physics_residuals, anomaly_data, fault_data, rul_data, health_score)
            fallback["llm_source"] = "Aerospace Propulsion Expert Heuristic Engine (Local Mode)"
            return fallback

    @classmethod
    def _query_openai(
        cls,
        api_key: str,
        telemetry: Dict[str, Any],
        physics_residuals: Dict[str, Any],
        anomaly_data: Dict[str, Any],
        fault_data: Dict[str, Any],
        rul_data: Dict[str, Any],
        health_score: float
    ) -> Dict[str, Any]:
        client = OpenAI(api_key=api_key)

        prompt = f"""
You are the Chief Propulsion & Flight Safety Engineer for a Military MALE UAV operating a turbocharged aero-piston engine (Rotax 914/915 class).
Analyze the following synchronized Digital Twin telemetry, physics residuals, AI anomaly scores, and fault classifications:

--- TELEMETRY DATA ---
RPM: {telemetry.get('rpm')}
EGT: {telemetry.get('egt')} °C
CHT: {telemetry.get('cht')} °C
Oil Temp: {telemetry.get('oil_temp')} °C
Oil Pressure: {telemetry.get('oil_press')} PSI
Fuel Flow: {telemetry.get('fuel_flow')} L/h
Altitude: {telemetry.get('altitude')} ft
Throttle: {telemetry.get('throttle')} %
Ambient Temp: {telemetry.get('ambient_temp')} °C
Mission Phase: {telemetry.get('mission_phase')}

--- PHYSICS RESIDUALS (Actual - Expected) ---
EGT Residual: {physics_residuals.get('egt_residual')} °C
CHT Residual: {physics_residuals.get('cht_residual')} °C
Oil Pressure Residual: {physics_residuals.get('oil_p_residual')} PSI
Fuel Flow Residual: {physics_residuals.get('fuel_residual')} L/h

--- AI ANALYTICS ---
Health Score: {health_score} / 100
Anomaly Status: {anomaly_data.get('anomaly_status')} (Score: {anomaly_data.get('anomaly_score')})
Top Outlier Feature: {anomaly_data.get('top_contributor')}
Predicted Fault: {fault_data.get('predicted_fault')} (Confidence: {fault_data.get('confidence_pct')}%)
RUL Remaining Hours: {rul_data.get('hours_remaining')} hrs
50-Hour In-Flight Failure Probability: {rul_data.get('failure_probability_50h_pct')}%

Respond strictly with a valid JSON object with the following four keys:
{{
  "ai_maintenance_report": "Detailed engineering summary of engine condition, wear accumulation, and subsystem integrity.",
  "ai_mission_risk_assessment": "Assessment of flight risks (e.g., In-Flight Engine Shutdown risk, loss of climb performance) during the current mission phase.",
  "ai_root_cause_analysis": "Physics-informed root cause explanation linking observed residuals and telemetry deviations to mechanical/thermal causes.",
  "ai_recommended_actions": [
    "Immediate action for UAV ground control station pilot",
    "Post-flight ground maintenance crew inspection task",
    "Long-term depot level overhaul or component replacement step"
  ]
}}
"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a specialized UAV Aero-Piston Propulsion AI Diagnostic system. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        parsed["llm_source"] = f"OpenAI ({settings.openai_model})"
        return parsed

    @classmethod
    def _aerospace_expert_fallback(
        cls,
        telemetry: Dict[str, Any],
        physics_residuals: Dict[str, Any],
        anomaly_data: Dict[str, Any],
        fault_data: Dict[str, Any],
        rul_data: Dict[str, Any],
        health_score: float
    ) -> Dict[str, Any]:
        fault = fault_data.get("predicted_fault", "Nominal Operation")
        confidence = fault_data.get("confidence_pct", 95.0)
        phase = telemetry.get("mission_phase", "Cruise")
        cht = telemetry.get("cht", 160.0)
        oil_p = telemetry.get("oil_press", 55.0)
        oil_t = telemetry.get("oil_temp", 85.0)
        hours = rul_data.get("hours_remaining", 1000.0)
        fail_prob = rul_data.get("failure_probability_50h_pct", 5.0)

        if fault == "Cooling Failure" or cht > 230.0:
            report = f"CRITICAL THERMAL ALERT: Cylinder Head Temperature is severely elevated at {cht}°C with a CHT residual of +{physics_residuals.get('cht_residual', 0)}°C above the aerodynamic cooling baseline. Heat dissipation capacity has collapsed."
            risk = f"EXTREME RISK during {phase}: Elevated CHT poses imminent cylinder bore scoring, piston seizure, and catastrophic In-Flight Engine Shutdown (IFSD). Mission safety factor degraded to CRITICAL."
            root_cause = "Loss of radiator airflow, coolant pump cavitational failure, or detached cylinder baffle seal leading to localized thermal boundary layer breakdown."
            actions = [
                "PILOT ACTION: Reduce throttle to lowest safe cruise power (55%), enrich mixture if controllable, and initiate immediate RTB (Return to Base).",
                "GROUND CREW: Inspect liquid cooling circuit for hose delamination, coolant expansion tank pressure cap, and radiator cowlings for foreign object debris.",
                "DEPOT ACTION: Perform borescopic inspection of cylinder barrels #2 and #4 for micro-scuffing before clearing aircraft for return to service."
            ]
        elif fault == "Lubrication Issue" or oil_p < 25.0:
            report = f"CRITICAL LUBRICATION ALERT: Engine oil pressure has plunged to {oil_p} PSI while oil temperature has spiked to {oil_t}°C. Hydrodynamic oil film thickness is critically degraded."
            risk = f"CATASTROPHIC MECHANICAL RISK during {phase}: Imminent connecting rod bearing wipe and crankshaft journal seizure. IFSD probability estimated at {fail_prob}%."
            root_cause = "Pressure relief valve stuck open, scavenge pump seal rupture, or external oil line rupture causing rapid lubricating fluid loss."
            actions = [
                "PILOT ACTION: Declare MAYDAY/Emergency. Plan immediate forced descent or nearest emergency landing field.",
                "GROUND CREW: Check scavenge pump pressure relief valve, oil filter element for bronze/steel metallic particulate flakes.",
                "DEPOT ACTION: Full teardown inspection of main bearings and crankshaft journals. Oil filter bypass valve bench testing."
            ]
        elif fault == "Injector Fault":
            report = f"COMBUSTION ANOMALY: Fuel flow deficit with EGT residual of {physics_residuals.get('egt_residual')}°C detected. Individual cylinder fuel injection unbalance identified with {confidence}% confidence."
            risk = f"MODERATE TO HIGH RISK during {phase}: Asymmetric thermal loading causing exhaust valve seat recession and localized detonation."
            root_cause = "Partially clogged electromagnetic injector nozzle, electrical solenoid harness intermittent resistance, or localized vapor lock."
            actions = [
                "PILOT ACTION: Monitor cylinder EGT balance closely. Avoid high-power climb settings.",
                "GROUND CREW: Perform ultrasonic cleaning and spray pattern bench calibration of all 4 fuel injectors.",
                "DEPOT ACTION: Replace fuel rail micro-filter and verify ECU injector driver current pulse wave with oscilloscope."
            ]
        elif fault == "Overheating":
            report = f"HIGH THERMAL STRESS: Both CHT ({cht}°C) and Oil Temperature ({oil_t}°C) exceed continuous operational limits. Overall health score depressed to {health_score}/100."
            risk = f"ELEVATED MISSION RISK: Continued operation at current throttle ({telemetry.get('throttle')}%) will cause rapid thermal fatigue and permanent metal temper degradation."
            root_cause = "Combination of sustained high throttle climb profile, high ambient thermal gradient, and restricted cowl air intake."
            actions = [
                "PILOT ACTION: Level off UAV to allow ram-air cooling; reduce throttle to 65% cruise power setting.",
                "GROUND CREW: Check intercooler and oil cooler duct seals for air leakage; flush cooling radiator.",
                "DEPOT ACTION: Measure compression ratio and check cylinder head torques to factory specification."
            ]
        else:
            report = f"NOMINAL AERO-PISTON HEALTH: Propulsion systems operating within certified operational envelopes. Digital Twin health score is {health_score}/100 with {hours} flight hours remaining until scheduled TBO."
            risk = f"LOW RISK: Engine demonstrates high stability during {phase}. 50-hour failure probability is nominal at {fail_prob}%."
            root_cause = "Thermodynamic cycles, volumetric efficiency, and lubrication film thickness are in full alignment with the physics baseline model."
            actions = [
                "PILOT ACTION: Continue nominal UAV flight plan and mission objectives.",
                "GROUND CREW: Standard 50-hour turn-around walk-around: inspect oil sight glass, verify throttle linkage safety wire.",
                "DEPOT ACTION: Log telemetry packet into squadron fleet health database for long-term trending."
            ]

        return {
            "ai_maintenance_report": report,
            "ai_mission_risk_assessment": risk,
            "ai_root_cause_analysis": root_cause,
            "ai_recommended_actions": actions
        }
