"""
MQTT Telemetry Adapter for Future ESP8266 Hardware Integration.

This module implements the TelemetryProvider interface. When hardware deployment
is ready, an ESP8266 running an MQTT client publishing JSON packets to
`aerotwin/uav/telemetry` can be connected here without altering any
Digital Twin, Physics, or AI analytics layers.
"""

from datetime import datetime, timezone
from typing import Optional, Callable
from backend.telemetry.models import TelemetryData, TelemetryUpdate, FaultInjection
from backend.telemetry.provider import TelemetryProvider

class MqttTelemetryProvider(TelemetryProvider):
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883, topic: str = "aerotwin/uav/telemetry"):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.connected = False
        self.latest_data: Optional[TelemetryData] = None

    def on_message_received(self, payload: dict):
        """Callback invoked when ESP8266 publishes telemetry JSON over MQTT."""
        try:
            self.latest_data = TelemetryData(
                timestamp=payload.get("timestamp", datetime.now(timezone.utc).isoformat()),
                rpm=payload.get("rpm", 5000.0),
                egt=payload.get("egt", 750.0),
                cht=payload.get("cht", 160.0),
                oil_temp=payload.get("oil_temp", 85.0),
                oil_press=payload.get("oil_press", 55.0),
                fuel_flow=payload.get("fuel_flow", 22.0),
                altitude=payload.get("altitude", 10000.0),
                ambient_temp=payload.get("ambient_temp", 15.0),
                humidity=payload.get("humidity", 50.0),
                throttle=payload.get("throttle", 70.0),
                mission_phase=payload.get("mission_phase", "Cruise"),
                source="esp8266_mqtt"
            )
        except Exception as e:
            print(f"Error parsing ESP8266 MQTT telemetry: {e}")

    def get_current_telemetry(self) -> TelemetryData:
        if self.latest_data:
            return self.latest_data
        # Fallback default until first packet
        return TelemetryData(
            rpm=5000.0, egt=750.0, cht=160.0, oil_temp=85.0,
            oil_press=55.0, fuel_flow=22.0, altitude=10000.0,
            ambient_temp=15.0, humidity=50.0, throttle=70.0,
            mission_phase="Cruise", source="esp8266_mqtt_standby"
        )

    def update_telemetry(self, update: TelemetryUpdate) -> TelemetryData:
        # Commands can be published back to ESP8266 via MQTT command topic
        return self.get_current_telemetry()

    def inject_fault(self, fault: FaultInjection) -> None:
        pass

    def step(self, dt: float) -> TelemetryData:
        return self.get_current_telemetry()
