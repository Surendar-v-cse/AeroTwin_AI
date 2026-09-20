from enum import Enum
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class MissionPhase(str, Enum):
    TAKEOFF = "Takeoff"
    CLIMB = "Climb"
    CRUISE = "Cruise"
    LOITER = "Loiter"
    DESCENT = "Descent"
    LANDING = "Landing"

class TelemetryData(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rpm: float = Field(..., ge=800, le=7500, description="Engine RPM (1000-7000 nominal)")
    egt: float = Field(..., ge=200, le=1000, description="Exhaust Gas Temp °C (300-900)")
    cht: float = Field(..., ge=30, le=350, description="Cylinder Head Temp °C (50-300)")
    oil_temp: float = Field(..., ge=10, le=170, description="Oil Temperature °C (20-150)")
    oil_press: float = Field(..., ge=5, le=130, description="Oil Pressure PSI (10-120)")
    fuel_flow: float = Field(..., ge=0, le=110, description="Fuel Flow L/h (0-100)")
    altitude: float = Field(..., ge=0, le=30000, description="Altitude ft (0-25000)")
    ambient_temp: float = Field(..., ge=-40, le=70, description="Ambient Temp °C (-20 to 60)")
    humidity: float = Field(..., ge=0, le=100, description="Humidity % (0-100)")
    throttle: float = Field(..., ge=0, le=100, description="Throttle Position % (0-100)")
    mission_phase: str = Field(default="Cruise", description="Mission Phase")
    source: str = Field(default="simulator", description="Source of telemetry ('simulator' or 'esp8266_mqtt')")

class TelemetryUpdate(BaseModel):
    rpm: Optional[float] = None
    egt: Optional[float] = None
    cht: Optional[float] = None
    oil_temp: Optional[float] = None
    oil_press: Optional[float] = None
    fuel_flow: Optional[float] = None
    altitude: Optional[float] = None
    ambient_temp: Optional[float] = None
    humidity: Optional[float] = None
    throttle: Optional[float] = None
    mission_phase: Optional[str] = None
    mode: Optional[str] = None  # "manual" or "auto"

class FaultInjection(BaseModel):
    fault_type: str = Field(..., description="Type of fault: 'injector_clog', 'oil_leak', 'cooling_duct_blockage', 'sensor_drift', 'none'")
    severity: float = Field(1.0, ge=0.0, le=1.0, description="Fault severity multiplier (0.0 - 1.0)")

class MissionScenarioRequest(BaseModel):
    scenario: str = Field(..., description="'high_altitude', 'hot_weather', 'endurance', 'emergency', 'nominal'")
