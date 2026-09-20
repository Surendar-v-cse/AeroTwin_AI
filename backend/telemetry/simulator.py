import math
import random
from datetime import datetime, timezone
from typing import Optional
from backend.telemetry.models import TelemetryData, TelemetryUpdate, FaultInjection, MissionPhase
from backend.telemetry.provider import TelemetryProvider

class SimulatorTelemetryProvider(TelemetryProvider):
    def __init__(self):
        self.mode = "auto"  # "auto" or "manual"
        self.active_fault = "none"
        self.fault_severity = 0.0

        # Internal persistent state
        self.throttle = 72.0          # %
        self.altitude = 12000.0       # ft
        self.ambient_temp = 15.0      # °C (ISA at sea level is 15°C)
        self.humidity = 45.0          # %
        self.mission_phase = MissionPhase.CRUISE.value

        # Physical engine states (with inertia)
        from backend.physics.engine_model import AeroPistonEnginePhysics
        init_rpm = 1200.0 + (self.throttle / 100.0) * 5400.0
        init_exp = AeroPistonEnginePhysics.calculate_expected_states(
            throttle=self.throttle,
            rpm=init_rpm,
            altitude=self.altitude,
            ambient_temp=self.ambient_temp,
            humidity=self.humidity
        )
        self.rpm = init_rpm
        self.egt = init_exp["expected_egt"]
        self.cht = init_exp["expected_cht"]
        self.oil_temp = init_exp["expected_oil_temp"]
        self.oil_press = init_exp["expected_oil_press"]
        self.fuel_flow = init_exp["expected_fuel_flow"]

        # Noise clock
        self.sim_time = 0.0

    def set_mode(self, mode: str):
        if mode in ("auto", "manual"):
            self.mode = mode

    def inject_fault(self, fault: FaultInjection):
        self.active_fault = fault.fault_type
        self.fault_severity = fault.severity

    def update_telemetry(self, update: TelemetryUpdate) -> TelemetryData:
        if update.mode is not None:
            self.set_mode(update.mode)

        if update.mission_phase is not None:
            self.mission_phase = update.mission_phase
            # If in auto mode, auto-tune throttle and altitude defaults for the phase
            if self.mode == "auto":
                self._apply_phase_defaults(update.mission_phase)

        if update.throttle is not None:
            self.throttle = max(0.0, min(100.0, update.throttle))
        if update.altitude is not None:
            self.altitude = max(0.0, min(25000.0, update.altitude))
        if update.ambient_temp is not None:
            self.ambient_temp = max(-20.0, min(60.0, update.ambient_temp))
        if update.humidity is not None:
            self.humidity = max(0.0, min(100.0, update.humidity))

        # In manual mode, user can directly adjust dynamic engine variables
        if self.mode == "manual":
            if update.rpm is not None:
                self.rpm = max(1000.0, min(7000.0, update.rpm))
            if update.egt is not None:
                self.egt = max(300.0, min(900.0, update.egt))
            if update.cht is not None:
                self.cht = max(50.0, min(300.0, update.cht))
            if update.oil_temp is not None:
                self.oil_temp = max(20.0, min(150.0, update.oil_temp))
            if update.oil_press is not None:
                self.oil_press = max(10.0, min(120.0, update.oil_press))
            if update.fuel_flow is not None:
                self.fuel_flow = max(0.0, min(100.0, update.fuel_flow))

        return self.get_current_telemetry()

    def _apply_phase_defaults(self, phase: str):
        if phase == MissionPhase.TAKEOFF.value:
            self.throttle = 100.0
            self.altitude = 150.0
        elif phase == MissionPhase.CLIMB.value:
            self.throttle = 90.0
            self.altitude = 6000.0
        elif phase == MissionPhase.CRUISE.value:
            self.throttle = 72.0
            self.altitude = 14000.0
        elif phase == MissionPhase.LOITER.value:
            self.throttle = 55.0
            self.altitude = 16000.0
        elif phase == MissionPhase.DESCENT.value:
            self.throttle = 35.0
            self.altitude = 5000.0
        elif phase == MissionPhase.LANDING.value:
            self.throttle = 25.0
            self.altitude = 200.0

    def step(self, dt: float = 0.5) -> TelemetryData:
        self.sim_time += dt

        if self.mode == "auto":
            # 1. Physics coupling: compute nominal equilibrium targets from first-principles physics model
            from backend.physics.engine_model import AeroPistonEnginePhysics
            target_rpm = 1200.0 + (self.throttle / 100.0) * 5400.0
            expected = AeroPistonEnginePhysics.calculate_expected_states(
                throttle=self.throttle,
                rpm=target_rpm,
                altitude=self.altitude,
                ambient_temp=self.ambient_temp,
                humidity=self.humidity
            )

            target_egt = expected["expected_egt"]
            target_cht = expected["expected_cht"]
            target_fuel = expected["expected_fuel_flow"]
            target_oil_temp = expected["expected_oil_temp"]
            target_oil_press = expected["expected_oil_press"]

            # 2. Compute Fault offsets
            f_sev = self.fault_severity
            fault_egt = 0.0
            fault_cht = 0.0
            fault_oil_t = 0.0
            fault_oil_p = 0.0
            fault_fuel = 0.0
            fault_rpm = 0.0

            if self.active_fault == "injector_clog":
                fault_egt = 85.0 * f_sev + math.sin(self.sim_time * 3.5) * 25.0 * f_sev
                fault_fuel = -4.2 * f_sev
                fault_rpm = -180.0 * f_sev
            elif self.active_fault == "oil_leak":
                fault_oil_p = -42.0 * f_sev
                fault_oil_t = 38.0 * f_sev
            elif self.active_fault == "cooling_duct_blockage":
                fault_cht = 85.0 * f_sev
                fault_oil_t = 22.0 * f_sev
            elif self.active_fault == "sensor_drift":
                fault_cht = 60.0 * math.sin(self.sim_time * 0.5) * f_sev
                fault_egt = 90.0 * math.cos(self.sim_time * 0.4) * f_sev

            target_rpm += fault_rpm
            target_egt += fault_egt
            target_cht += fault_cht
            target_oil_temp += fault_oil_t
            target_oil_press += fault_oil_p
            target_fuel += fault_fuel

            # Inertia smoothing (first-order lag)
            alpha_fast = 1.0 - math.exp(-dt / 1.2)     # fast response for RPM, Fuel
            alpha_thermal = 1.0 - math.exp(-dt / 3.5)  # thermal lag for CHT, Oil Temp

            self.rpm += alpha_fast * (target_rpm - self.rpm)
            self.fuel_flow += alpha_fast * (target_fuel - self.fuel_flow)
            self.egt += (1.0 - math.exp(-dt / 2.0)) * (target_egt - self.egt)
            self.cht += alpha_thermal * (target_cht - self.cht)
            self.oil_temp += alpha_thermal * (target_oil_temp - self.oil_temp)
            self.oil_press += alpha_fast * (target_oil_press - self.oil_press)

        # Clamp internal states to prevent numerical runaway
        self.rpm = max(1000.0, min(7000.0, self.rpm))
        self.egt = max(300.0, min(900.0, self.egt))
        self.cht = max(50.0, min(290.0, self.cht))
        self.oil_temp = max(20.0, min(148.0, self.oil_temp))
        self.oil_press = max(10.0, min(120.0, self.oil_press))
        self.fuel_flow = max(0.0, min(100.0, self.fuel_flow))

        # 3. Add realistic sensor jitter/noise (±0.3% to ±0.8%)
        noise_rpm = random.gauss(0, 8)
        noise_egt = random.gauss(0, 1.2)
        noise_cht = random.gauss(0, 0.6)
        noise_oil_t = random.gauss(0, 0.3)
        noise_oil_p = random.gauss(0, 0.4)
        noise_fuel = random.gauss(0, 0.1)

        # Clamp to realistic physical boundaries
        cur_rpm = max(1000.0, min(7000.0, self.rpm + noise_rpm))
        cur_egt = max(300.0, min(900.0, self.egt + noise_egt))
        cur_cht = max(50.0, min(295.0, self.cht + noise_cht))
        cur_oil_t = max(20.0, min(148.0, self.oil_temp + noise_oil_t))
        cur_oil_p = max(10.0, min(120.0, self.oil_press + noise_oil_p))
        cur_fuel = max(0.0, min(100.0, self.fuel_flow + noise_fuel))

        return TelemetryData(
            timestamp=datetime.now(timezone.utc).isoformat(),
            rpm=round(cur_rpm, 1),
            egt=round(cur_egt, 1),
            cht=round(cur_cht, 1),
            oil_temp=round(cur_oil_t, 1),
            oil_press=round(cur_oil_p, 1),
            fuel_flow=round(cur_fuel, 2),
            altitude=round(self.altitude, 1),
            ambient_temp=round(self.ambient_temp, 1),
            humidity=round(self.humidity, 1),
            throttle=round(self.throttle, 1),
            mission_phase=self.mission_phase,
            source="simulator"
        )

    def get_current_telemetry(self) -> TelemetryData:
        cur_rpm = max(1000.0, min(7000.0, self.rpm))
        cur_egt = max(300.0, min(900.0, self.egt))
        cur_cht = max(50.0, min(295.0, self.cht))
        cur_oil_t = max(20.0, min(148.0, self.oil_temp))
        cur_oil_p = max(10.0, min(120.0, self.oil_press))
        cur_fuel = max(0.0, min(100.0, self.fuel_flow))

        return TelemetryData(
            timestamp=datetime.now(timezone.utc).isoformat(),
            rpm=round(cur_rpm, 1),
            egt=round(cur_egt, 1),
            cht=round(cur_cht, 1),
            oil_temp=round(cur_oil_t, 1),
            oil_press=round(cur_oil_p, 1),
            fuel_flow=round(cur_fuel, 2),
            altitude=round(self.altitude, 1),
            ambient_temp=round(self.ambient_temp, 1),
            humidity=round(self.humidity, 1),
            throttle=round(self.throttle, 1),
            mission_phase=self.mission_phase,
            source="simulator"
        )
