from abc import ABC, abstractmethod
from typing import Optional
from backend.telemetry.models import TelemetryData, TelemetryUpdate, FaultInjection

class TelemetryProvider(ABC):
    """
    Abstract Telemetry Provider.
    Decouples telemetry sources so the Simulator can be seamlessly replaced
    or augmented by an ESP8266 MQTT client without modifying downstream layers.
    """

    @abstractmethod
    def get_current_telemetry(self) -> TelemetryData:
        """Returns the latest synchronized telemetry packet."""
        pass

    @abstractmethod
    def update_telemetry(self, update: TelemetryUpdate) -> TelemetryData:
        """Applies manual controls or mode adjustments."""
        pass

    @abstractmethod
    def inject_fault(self, fault: FaultInjection) -> None:
        """Injects a physical failure signature into the stream."""
        pass

    @abstractmethod
    def step(self, dt: float) -> TelemetryData:
        """Advances the telemetry state by dt seconds."""
        pass
