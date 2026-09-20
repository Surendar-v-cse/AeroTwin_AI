from collections import deque
from typing import Dict, Any, List
from backend.telemetry.models import TelemetryData

class TrendAnalysisEngine:
    """
    Tracks rolling parameter trajectories, calculating derivatives
    (e.g., d(CHT)/dt, d(OilTemp)/dt), variance, and directional trend flags.
    """

    def __init__(self, window_size: int = 40):
        self.history = deque(maxlen=window_size)

    def update(self, telem: TelemetryData, health_score: float) -> Dict[str, Any]:
        snapshot = {
            "timestamp": telem.timestamp,
            "cht": telem.cht,
            "egt": telem.egt,
            "oil_temp": telem.oil_temp,
            "oil_press": telem.oil_press,
            "fuel_flow": telem.fuel_flow,
            "health_score": health_score
        }
        self.history.append(snapshot)

        if len(self.history) < 4:
            return {
                "temperature_trend": "Stable",
                "oil_trend": "Stable",
                "fuel_trend": "Stable",
                "health_trend": "Stable",
                "d_cht_dt": 0.0,
                "d_oil_t_dt": 0.0,
                "d_health_dt": 0.0,
                "recent_history": list(self.history)
            }

        # Calculate rate of change over recent samples (~5 seconds window)
        n_samples = min(len(self.history), 10)
        recent = list(self.history)[-n_samples:]

        d_cht = recent[-1]["cht"] - recent[0]["cht"]
        d_egt = recent[-1]["egt"] - recent[0]["egt"]
        d_oil_t = recent[-1]["oil_temp"] - recent[0]["oil_temp"]
        d_oil_p = recent[-1]["oil_press"] - recent[0]["oil_press"]
        d_fuel = recent[-1]["fuel_flow"] - recent[0]["fuel_flow"]
        d_health = recent[-1]["health_score"] - recent[0]["health_score"]

        # Trend flags
        if d_cht > 12.0 or d_egt > 35.0:
            temp_trend = "Rapidly Rising (Thermal Surge)"
        elif d_cht < -12.0 or d_egt < -35.0:
            temp_trend = "Cooling Down"
        else:
            temp_trend = "Thermal Equilibrium"

        if d_oil_p < -8.0 and d_oil_t > 5.0:
            oil_trend = "Degrading (Pressure Drop & Temp Rise)"
        elif d_oil_t > 10.0:
            oil_trend = "Overheating"
        else:
            oil_trend = "Nominal Lubrication"

        if abs(d_fuel) > 4.0:
            fuel_trend = "Fluctuating Demand"
        else:
            fuel_trend = "Steady Consumption"

        if d_health < -8.0:
            health_trend = "Deteriorating Rapidly"
        elif d_health > 5.0:
            health_trend = "Recovering"
        else:
            health_trend = "Steady Condition"

        return {
            "temperature_trend": temp_trend,
            "oil_trend": oil_trend,
            "fuel_trend": fuel_trend,
            "health_trend": health_trend,
            "d_cht_dt": round(d_cht / (n_samples * 0.5), 2),  # °C / sec
            "d_oil_t_dt": round(d_oil_t / (n_samples * 0.5), 2),
            "d_health_dt": round(d_health / (n_samples * 0.5), 2),
            "recent_history": list(self.history)[-20:]
        }
