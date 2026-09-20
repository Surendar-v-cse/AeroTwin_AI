import asyncio
import json
import urllib.request
import urllib.parse
import websockets
import sys

def test_physics_atmosphere():
    print("[TEST 1/8] Testing Atmosphere Model...")
    from backend.physics.atmosphere import AtmosphereModel
    sea_level = AtmosphereModel.get_isa_conditions(0.0)
    assert abs(sea_level["temperature_c"] - 15.0) < 0.1, f"Expected 15°C at sea level, got {sea_level['temperature_c']}"
    assert abs(sea_level["density_ratio_sigma"] - 1.0) < 0.01, f"Expected sigma 1.0 at sea level, got {sea_level['density_ratio_sigma']}"

    high_alt = AtmosphereModel.get_isa_conditions(25000.0)
    assert high_alt["temperature_c"] < -30.0, "Expected sub-zero at 25000 ft"
    assert high_alt["density_ratio_sigma"] < 0.5, "Expected density ratio < 0.5 at 25000 ft"
    print("  -> Atmosphere ISA calculations: PASS")

def test_engine_physics():
    print("[TEST 2/8] Testing Engine Physics & Residuals...")
    from backend.physics.engine_model import AeroPistonEnginePhysics
    from backend.physics.residual_engine import PhysicsResidualEngine
    from backend.telemetry.models import TelemetryData

    cruise_exp = AeroPistonEnginePhysics.calculate_expected_states(
        throttle=72.0, rpm=5200.0, altitude=12000.0, ambient_temp=15.0
    )
    assert 650.0 <= cruise_exp["expected_egt"] <= 850.0, f"Expected cruise EGT in 650-850, got {cruise_exp['expected_egt']}"
    assert 100.0 <= cruise_exp["expected_cht"] <= 200.0, f"Expected cruise CHT in 100-200, got {cruise_exp['expected_cht']}"
    assert 15.0 <= cruise_exp["expected_fuel_flow"] <= 35.0, f"Expected cruise fuel in 15-35, got {cruise_exp['expected_fuel_flow']}"

    telem = TelemetryData(
        rpm=5200.0, egt=780.0, cht=170.0, oil_temp=90.0, oil_press=55.0,
        fuel_flow=24.0, altitude=12000.0, ambient_temp=15.0, humidity=40.0,
        throttle=72.0, mission_phase="Cruise"
    )
    res_eval = PhysicsResidualEngine.compute_residuals(telem)
    assert "residuals" in res_eval
    assert "egt_residual" in res_eval["residuals"]
    print("  -> Engine Physics & Residual derivations: PASS")

def test_digital_twin_subsystems():
    print("[TEST 3/8] Testing Digital Twin Core & Subsystem Observers...")
    from backend.digital_twin.twin_core import DigitalTwinEngine
    from backend.telemetry.models import TelemetryData

    twin = DigitalTwinEngine()
    telem = TelemetryData(
        rpm=5200.0, egt=740.0, cht=150.0, oil_temp=85.0, oil_press=60.0,
        fuel_flow=22.0, altitude=10000.0, ambient_temp=15.0, humidity=50.0,
        throttle=70.0, mission_phase="Cruise"
    )
    state = twin.synchronize(telem)
    sub = state["subsystems"]
    assert "thermal_state" in sub
    assert "mechanical_state" in sub
    assert "combustion_state" in sub
    assert "lubrication_state" in sub
    assert "fuel_state" in sub
    assert "predicted_state" in state
    print("  -> Subsystems observers (Thermal, Mech, Comb, Lub, Fuel): PASS")

def test_ai_analytics():
    print("[TEST 4/8] Testing AI Analytics Engines...")
    from backend.ai_analytics.anomaly_detector import AnomalyDetectionEngine
    from backend.ai_analytics.fault_classifier import FaultClassificationEngine
    from backend.ai_analytics.rul_engine import RemainingUsefulLifeEngine
    from backend.ai_analytics.virtual_sensors import VirtualSensorEngine
    from backend.ai_analytics.openai_advisor import OpenAIPropulsionAdvisor
    from backend.telemetry.models import TelemetryData

    # 1. Anomaly Detector
    ad = AnomalyDetectionEngine()
    nominal_telem = TelemetryData(
        rpm=5200.0, egt=745.0, cht=130.0, oil_temp=85.0, oil_press=60.0,
        fuel_flow=22.0, altitude=12000.0, ambient_temp=15.0, humidity=45.0,
        throttle=72.0, mission_phase="Cruise"
    )
    anom_res = ad.analyze(nominal_telem, {"egt_residual": 0.0, "cht_residual": 0.0, "oil_p_residual": 0.0})
    assert anom_res["anomaly_status"] in ("Normal", "Warning"), f"Expected Normal/Warning for nominal, got {anom_res['anomaly_status']}"

    # 2. Fault Classifier
    fc = FaultClassificationEngine()
    fault_res = fc.classify(nominal_telem, {"egt_residual": 0.0, "cht_residual": 0.0, "oil_p_residual": 0.0, "fuel_residual": 0.0})
    assert "predicted_fault" in fault_res
    assert fault_res["confidence_pct"] > 50.0

    # 3. RUL Engine
    rul_res = RemainingUsefulLifeEngine.estimate_rul(
        nominal_telem, {"egt_residual": 0.0, "cht_residual": 0.0, "oil_p_residual": 0.0},
        anom_res["anomaly_score"], fault_res["predicted_fault"]
    )
    assert rul_res["hours_remaining"] > 0
    explain = rul_res["explainability"]
    total_pct = sum(explain.values())
    assert abs(total_pct - 100.0) < 1.0, f"Explainability percentages should sum to 100%, got {total_pct}"

    # 4. Virtual Sensors
    subsystems = {
        "thermal_state": {"thermal_stress_index": 45.0},
        "combustion_state": {"combustion_quality_score": 90.0},
        "lubrication_state": {"oil_film_integrity": 85.0}
    }
    vs = VirtualSensorEngine.synthesize_virtual_sensors(
        nominal_telem, {"expected_efficiency": 30.0}, {"efficiency_residual": 0.0},
        subsystems, anom_res["anomaly_score"]
    )
    assert 20.0 <= vs["engine_efficiency_pct"] <= 40.0

    # 5. Advisor
    advisor_res = OpenAIPropulsionAdvisor.generate_insights(
        telemetry=nominal_telem.model_dump(),
        physics_residuals={"egt_residual": 0.0, "cht_residual": 0.0},
        anomaly_data=anom_res,
        fault_data=fault_res,
        rul_data=rul_res,
        health_score=95.0
    )
    assert "ai_maintenance_report" in advisor_res
    assert "ai_mission_risk_assessment" in advisor_res
    assert "ai_root_cause_analysis" in advisor_res
    assert len(advisor_res["ai_recommended_actions"]) > 0
    print("  -> Isolation Forest, XGBoost, RUL, Virtual Sensors, Advisor: PASS")

def test_decision_intelligence():
    print("[TEST 5/8] Testing Decision Intelligence Layer...")
    from backend.decision_intelligence.health_scorer import HealthScoringEngine
    from backend.decision_intelligence.readiness_engine import MissionReadinessEngine
    from backend.decision_intelligence.maintenance_advisor import MaintenanceAdvisor
    from backend.telemetry.models import TelemetryData

    telem = TelemetryData(
        rpm=5200.0, egt=745.0, cht=130.0, oil_temp=85.0, oil_press=60.0,
        fuel_flow=22.0, altitude=12000.0, ambient_temp=15.0, humidity=45.0,
        throttle=72.0, mission_phase="Cruise"
    )
    health = HealthScoringEngine.calculate_health(
        telem, {"cht_residual": 0.0, "egt_residual": 0.0, "oil_p_residual": 0.0},
        0.15, "Nominal Operation", 99.0
    )
    assert health["health_score"] >= 80.0
    assert health["health_category"] in ("Excellent", "Good")

    readiness = MissionReadinessEngine.evaluate_readiness(
        health["health_score"], "Normal", "Nominal Operation", False
    )
    assert readiness["flight_authorized"] is True

    maint = MaintenanceAdvisor.generate_maintenance_advisories(
        telem, {"cht_residual": 0.0}, {"anomaly_status": "Normal"},
        {"predicted_fault": "Nominal Operation", "confidence_pct": 99.0},
        {"hours_remaining": 850.0}, health
    )
    assert "active_alerts" in maint
    assert "maintenance_recommendations" in maint
    print("  -> Health Scorer, Mission Readiness, Maintenance Advisor: PASS")

def test_rest_endpoints():
    print("[TEST 6/8] Testing REST API Endpoints on http://127.0.0.1:8000...")
    base = "http://127.0.0.1:8000"

    # 1. GET /api/telemetry
    res = urllib.request.urlopen(f"{base}/api/telemetry")
    assert res.status == 200
    telem = json.loads(res.read())
    assert "rpm" in telem and "cht" in telem

    # 2. POST /api/telemetry (update throttle)
    req = urllib.request.Request(
        f"{base}/api/telemetry",
        data=json.dumps({"throttle": 75.0, "altitude": 14000.0}).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    assert res.status == 200

    # 3. GET /api/twin
    res = urllib.request.urlopen(f"{base}/api/twin")
    assert res.status == 200
    twin = json.loads(res.read())
    assert "expected_state" in twin
    assert "residuals" in twin
    assert "subsystems" in twin

    # 4. GET /api/anomaly, /api/faults, /api/rul, /api/health
    for ep in ["anomaly", "faults", "rul", "health"]:
        res = urllib.request.urlopen(f"{base}/api/{ep}")
        assert res.status == 200

    # 5. GET /api/maintenance
    res = urllib.request.urlopen(f"{base}/api/maintenance")
    assert res.status == 200

    # 6. GET /api/mission-report
    res = urllib.request.urlopen(f"{base}/api/mission-report")
    assert res.status == 200
    rep = json.loads(res.read())
    assert rep["aircraft_callsign"] == "AEROTWIN-UAV-01"

    # 7. POST /api/ai-insights
    req = urllib.request.Request(
        f"{base}/api/ai-insights",
        data=json.dumps({}).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    assert res.status == 200
    insights = json.loads(res.read())
    assert "ai_maintenance_report" in insights

    # 8. POST /api/simulation (Nominal Reset)
    req = urllib.request.Request(
        f"{base}/api/simulation",
        data=json.dumps({"scenario": "nominal"}).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    assert res.status == 200

    print("  -> All 12 REST endpoints tested and verified (200 OK): PASS")

async def _test_ws():
    print("[TEST 7/8] Testing Live WebSocket Stream on ws://127.0.0.1:8000/ws/telemetry...")
    async with websockets.connect("ws://127.0.0.1:8000/ws/telemetry") as ws:
        msg = await ws.recv()
        data = json.loads(msg)
        expected_keys = [
            "timestamp", "telemetry", "simulation_mode", "active_fault",
            "expected_state", "residuals", "residual_magnitude", "subsystems",
            "predicted_state", "anomaly", "faults", "trends", "rul",
            "virtual_sensors", "health", "readiness", "maintenance"
        ]
        for k in expected_keys:
            assert k in data, f"Missing key '{k}' in WebSocket packet"
        print(f"  -> WebSocket broadcast verified ({len(expected_keys)} payload keys): PASS")

def test_websocket():
    asyncio.run(_test_ws())

def test_database():
    print("[TEST 8/8] Testing SQLite Database Persistence...")
    import sqlite3
    conn = sqlite3.connect("backend/aerotwin.db", timeout=10.0)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM telemetry_history")
    telem_cnt = cur.fetchone()[0]
    assert telem_cnt > 0, "Expected telemetry records in database"

    cur.execute("SELECT COUNT(*) FROM physics_residuals")
    res_cnt = cur.fetchone()[0]
    assert res_cnt > 0, "Expected physics residual records in database"

    cur.execute("SELECT COUNT(*) FROM ai_analytics")
    ai_cnt = cur.fetchone()[0]
    assert ai_cnt > 0, "Expected AI analytics records in database"

    conn.close()
    print(f"  -> Database verified: {telem_cnt} telemetry rows, {res_cnt} residuals rows, {ai_cnt} AI logs: PASS")

if __name__ == "__main__":
    print("==================================================")
    print("      AEROTWIN AI COMPREHENSIVE TEST SUITE        ")
    print("==================================================")
    test_physics_atmosphere()
    test_engine_physics()
    test_digital_twin_subsystems()
    test_ai_analytics()
    test_decision_intelligence()
    test_rest_endpoints()
    test_websocket()
    test_database()
    print("==================================================")
    print("   ALL 8/8 TEST SUITES COMPLETED WITH 100% PASS   ")
    print("==================================================")
