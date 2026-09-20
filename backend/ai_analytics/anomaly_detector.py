import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List
from backend.telemetry.models import TelemetryData

class AnomalyDetectionEngine:
    """
    AI Anomaly Detection Engine using Scikit-Learn Isolation Forest.
    Trained on nominal aero-engine operating conditions coupled with physics residuals.
    Outputs: Anomaly Score (0.0 to 1.0), Status (Normal, Warning, Critical), and Top Outlier Feature.
    """

    FEATURE_NAMES = [
        "rpm", "egt", "cht", "oil_temp", "oil_press", "fuel_flow",
        "egt_residual", "cht_residual", "oil_p_residual"
    ]

    def __init__(self):
        self.model = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        self._fit_nominal_baseline()

    def _fit_nominal_baseline(self):
        """Generates synthetic baseline nominal flight envelope data and fits the IsolationForest."""
        np.random.seed(42)
        n_samples = 1500

        # Nominal flight distribution across various throttle settings (40% to 85%)
        throttles = np.random.uniform(40, 85, n_samples)
        rpm = 1200 + (throttles / 100.0) * 5400 + np.random.normal(0, 40, n_samples)
        egt = 650 + (throttles / 100.0) * 120 + np.random.normal(0, 15, n_samples)
        cht = 130 + (throttles / 100.0) * 45 + np.random.normal(0, 8, n_samples)
        oil_temp = 75 + (throttles / 100.0) * 20 + np.random.normal(0, 4, n_samples)
        oil_press = 50 + (rpm / 6000.0) * 20 + np.random.normal(0, 3, n_samples)
        fuel_flow = (throttles / 100.0) * 28 + np.random.normal(0, 1.0, n_samples)

        # Nominal physics residuals should be tightly centered near zero
        egt_res = np.random.normal(0, 8.0, n_samples)
        cht_res = np.random.normal(0, 4.0, n_samples)
        oil_p_res = np.random.normal(0, 2.5, n_samples)

        X_nominal = np.column_stack([
            rpm, egt, cht, oil_temp, oil_press, fuel_flow,
            egt_res, cht_res, oil_p_res
        ])
        self.model.fit(X_nominal)

    def analyze(self, telem: TelemetryData, residuals: Dict[str, float]) -> Dict[str, Any]:
        features = np.array([[
            telem.rpm,
            telem.egt,
            telem.cht,
            telem.oil_temp,
            telem.oil_press,
            telem.fuel_flow,
            residuals.get("egt_residual", 0.0),
            residuals.get("cht_residual", 0.0),
            residuals.get("oil_p_residual", 0.0)
        ]])

        # Decision function: lower values mean more anomalous; positive values are inliers
        raw_score = float(self.model.decision_function(features)[0])
        if raw_score >= 0.0:
            anomaly_score = float(max(0.04, 0.20 - raw_score * 1.2))
        else:
            anomaly_score = float(np.clip(0.25 + abs(raw_score) * 4.5, 0.25, 1.0))

        # Secondary check for extreme physical threshold breaches
        is_hard_breach = (
            telem.cht > 240.0 or telem.egt > 875.0 or
            telem.oil_press < 22.0 or telem.oil_temp > 135.0 or
            abs(residuals.get("cht_residual", 0.0)) > 45.0
        )
        if is_hard_breach:
            anomaly_score = max(anomaly_score, 0.88)

        if anomaly_score >= 0.65:
            status = "Critical"
        elif anomaly_score >= 0.35:
            status = "Warning"
        else:
            status = "Normal"

        # Determine top contributing feature
        feature_deviations = {
            "Exhaust Gas Temp (EGT)": abs(residuals.get("egt_residual", 0.0)) / 15.0,
            "Cylinder Head Temp (CHT)": abs(residuals.get("cht_residual", 0.0)) / 10.0,
            "Oil Pressure": abs(residuals.get("oil_p_residual", 0.0)) / 5.0,
            "Fuel Flow": abs(residuals.get("fuel_residual", 0.0)) / 3.0,
            "Engine RPM": abs(telem.rpm - 5200.0) / 1500.0
        }
        top_contributor = max(feature_deviations, key=feature_deviations.get)

        return {
            "anomaly_score": round(anomaly_score, 3),
            "anomaly_status": status,
            "raw_decision_score": round(float(raw_score), 4),
            "top_contributor": top_contributor,
            "confidence_pct": round(float(abs(raw_score) * 100.0 + 50.0), 1)
        }
