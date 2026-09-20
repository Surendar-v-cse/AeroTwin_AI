import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Telemetry History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        rpm REAL NOT NULL,
        egt REAL NOT NULL,
        cht REAL NOT NULL,
        oil_temp REAL NOT NULL,
        oil_press REAL NOT NULL,
        fuel_flow REAL NOT NULL,
        altitude REAL NOT NULL,
        ambient_temp REAL NOT NULL,
        humidity REAL NOT NULL,
        throttle REAL NOT NULL,
        mission_phase TEXT NOT NULL,
        source TEXT NOT NULL DEFAULT 'simulator'
    );
    """)

    # Digital Twin States
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS digital_twin_states (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        thermal_state TEXT NOT NULL,
        mechanical_state TEXT NOT NULL,
        combustion_state TEXT NOT NULL,
        lubrication_state TEXT NOT NULL,
        fuel_state TEXT NOT NULL,
        virtual_sensors TEXT NOT NULL
    );
    """)

    # Physics Residuals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS physics_residuals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        egt_residual REAL NOT NULL,
        cht_residual REAL NOT NULL,
        fuel_residual REAL NOT NULL,
        oil_p_residual REAL NOT NULL,
        thermal_stress_residual REAL NOT NULL,
        efficiency REAL NOT NULL
    );
    """)

    # AI Analytics Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        anomaly_score REAL NOT NULL,
        anomaly_status TEXT NOT NULL,
        predicted_fault TEXT NOT NULL,
        fault_confidence REAL NOT NULL,
        rul_hours REAL NOT NULL,
        failure_prob REAL NOT NULL
    );
    """)

    # Maintenance Logs & Recommendations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        log_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        title TEXT NOT NULL,
        details TEXT NOT NULL,
        recommended_actions TEXT NOT NULL,
        ai_generated INTEGER DEFAULT 0
    );
    """)

    # Mission Simulations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mission_simulations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        mission_type TEXT NOT NULL,
        duration_seconds REAL NOT NULL,
        summary TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def log_telemetry_record(telem: Dict[str, Any]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO telemetry_history (
            timestamp, rpm, egt, cht, oil_temp, oil_press, fuel_flow,
            altitude, ambient_temp, humidity, throttle, mission_phase, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        telem.get("timestamp", datetime.now(timezone.utc).isoformat()),
        telem["rpm"], telem["egt"], telem["cht"], telem["oil_temp"],
        telem["oil_press"], telem["fuel_flow"], telem["altitude"],
        telem["ambient_temp"], telem["humidity"], telem["throttle"],
        telem["mission_phase"], telem.get("source", "simulator")
    ))
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def log_twin_record(twin_data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO digital_twin_states (
            timestamp, thermal_state, mechanical_state, combustion_state,
            lubrication_state, fuel_state, virtual_sensors
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        twin_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        json.dumps(twin_data.get("thermal_state", {})),
        json.dumps(twin_data.get("mechanical_state", {})),
        json.dumps(twin_data.get("combustion_state", {})),
        json.dumps(twin_data.get("lubrication_state", {})),
        json.dumps(twin_data.get("fuel_state", {})),
        json.dumps(twin_data.get("virtual_sensors", {}))
    ))
    conn.commit()
    conn.close()

def log_residuals_record(res: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO physics_residuals (
            timestamp, egt_residual, cht_residual, fuel_residual,
            oil_p_residual, thermal_stress_residual, efficiency
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        res.get("timestamp", datetime.now(timezone.utc).isoformat()),
        res.get("egt_residual", 0.0),
        res.get("cht_residual", 0.0),
        res.get("fuel_residual", 0.0),
        res.get("oil_p_residual", 0.0),
        res.get("thermal_stress_residual", 0.0),
        res.get("efficiency", 0.0)
    ))
    conn.commit()
    conn.close()

def log_ai_record(ai_data: Dict[str, Any]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_analytics (
            timestamp, anomaly_score, anomaly_status, predicted_fault,
            fault_confidence, rul_hours, failure_prob
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        ai_data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        ai_data.get("anomaly_score", 0.0),
        ai_data.get("anomaly_status", "Normal"),
        ai_data.get("predicted_fault", "Nominal"),
        ai_data.get("fault_confidence", 100.0),
        ai_data.get("rul_hours", 1200.0),
        ai_data.get("failure_prob", 0.0)
    ))
    conn.commit()
    conn.close()

def get_recent_telemetry(limit: int = 60) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM telemetry_history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return list(reversed(rows))

def get_recent_residuals(limit: int = 60) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM physics_residuals ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return list(reversed(rows))
