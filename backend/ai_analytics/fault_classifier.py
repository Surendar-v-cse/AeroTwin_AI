import numpy as np
from typing import Dict, Any, List
try:
    from xgboost import XGBClassifier
    USE_XGB = True
except ImportError:
    from sklearn.ensemble import RandomForestClassifier
    USE_XGB = False

from backend.telemetry.models import TelemetryData

class FaultClassificationEngine:
    """
    AI Fault Classification Engine.
    Classifies engine health into 8 operational states:
    - Nominal Operation
    - Injector Fault
    - Lubrication Issue
    - Cooling Failure
    - Combustion Instability
    - Sensor Failure
    - Overheating
    - Fuel System Degradation
    """

    FAULT_CLASSES = [
        "Nominal Operation",
        "Injector Fault",
        "Lubrication Issue",
        "Cooling Failure",
        "Combustion Instability",
        "Sensor Failure",
        "Overheating",
        "Fuel System Degradation"
    ]

    def __init__(self):
        if USE_XGB:
            self.model = XGBClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                eval_metric="mlogloss"
            )
        else:
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)

        self._train_fault_signatures()

    def _train_fault_signatures(self):
        """Generates physics-grounded synthetic training sets for each failure mode and fits the model."""
        np.random.seed(42)
        n_per_class = 300
        X_all = []
        y_all = []

        # Features: [rpm, egt, cht, oil_temp, oil_press, fuel_flow, egt_res, cht_res, oil_p_res, fuel_res]
        for class_idx, class_name in enumerate(self.FAULT_CLASSES):
            for _ in range(n_per_class):
                # Baseline cruise
                rpm = np.random.uniform(4800, 5600)
                egt = np.random.uniform(710, 760)
                cht = np.random.uniform(150, 175)
                oil_t = np.random.uniform(80, 92)
                oil_p = np.random.uniform(52, 65)
                fuel = np.random.uniform(22, 26)
                egt_r = np.random.normal(0, 5)
                cht_r = np.random.normal(0, 4)
                oil_p_r = np.random.normal(0, 2)
                fuel_r = np.random.normal(0, 0.5)

                if class_name == "Nominal Operation":
                    pass
                elif class_name == "Injector Fault":
                    egt += np.random.uniform(70, 140)
                    egt_r += np.random.uniform(60, 130)
                    fuel -= np.random.uniform(3, 7)
                    fuel_r -= np.random.uniform(3, 6)
                elif class_name == "Lubrication Issue":
                    oil_p = np.random.uniform(12, 28)
                    oil_p_r = -np.random.uniform(25, 45)
                    oil_t += np.random.uniform(25, 55)
                elif class_name == "Cooling Failure":
                    cht += np.random.uniform(65, 115)
                    cht_r += np.random.uniform(60, 110)
                    oil_t += np.random.uniform(15, 30)
                elif class_name == "Combustion Instability":
                    egt_r += np.random.normal(0, 50)
                    rpm += np.random.normal(0, 220)
                    fuel_r += np.random.normal(0, 4)
                elif class_name == "Sensor Failure":
                    # Frozen or thermodynamically impossible (e.g., EGT 300°C at 6500 RPM)
                    egt = np.random.choice([250.0, 950.0])
                    egt_r = np.random.choice([-300.0, 250.0])
                elif class_name == "Overheating":
                    cht += np.random.uniform(55, 95)
                    cht_r += np.random.uniform(50, 90)
                    oil_t += np.random.uniform(35, 55)
                    egt += np.random.uniform(40, 75)
                elif class_name == "Fuel System Degradation":
                    fuel -= np.random.uniform(6, 12)
                    fuel_r -= np.random.uniform(6, 11)
                    rpm -= np.random.uniform(400, 900)

                features = [rpm, egt, cht, oil_t, oil_p, fuel, egt_r, cht_r, oil_p_r, fuel_r]
                X_all.append(features)
                y_all.append(class_idx)

        X_mat = np.array(X_all)
        y_vec = np.array(y_all)
        self.model.fit(X_mat, y_vec)

    def classify(self, telem: TelemetryData, residuals: Dict[str, float]) -> Dict[str, Any]:
        features = np.array([[
            telem.rpm,
            telem.egt,
            telem.cht,
            telem.oil_temp,
            telem.oil_press,
            telem.fuel_flow,
            residuals.get("egt_residual", 0.0),
            residuals.get("cht_residual", 0.0),
            residuals.get("oil_p_residual", 0.0),
            residuals.get("fuel_residual", 0.0)
        ]])

        probs = self.model.predict_proba(features)[0]
        top_idx = int(np.argmax(probs))
        top_fault = self.FAULT_CLASSES[top_idx]
        confidence = float(probs[top_idx] * 100.0)

        # Build full probability distribution dictionary
        distribution = {
            fault_name: round(float(probs[i] * 100.0), 1)
            for i, fault_name in enumerate(self.FAULT_CLASSES)
        }

        # Severity ranking
        is_critical = top_fault in ("Cooling Failure", "Lubrication Issue", "Overheating") and confidence > 60.0

        return {
            "predicted_fault": top_fault,
            "confidence_pct": round(confidence, 1),
            "is_critical": is_critical,
            "probability_distribution": distribution,
            "model_type": "XGBoost" if USE_XGB else "RandomForest"
        }
