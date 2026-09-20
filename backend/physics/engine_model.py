import math
from typing import Dict, Any
from backend.physics.atmosphere import AtmosphereModel

class AeroPistonEnginePhysics:
    """
    Thermodynamic and aerodynamic physics model for a turbocharged
    MALE UAV 4-cylinder aero-piston engine (Rotax 914/915 iS class).
    Calculates expected engine states based on first-principles physics.
    """

    # Engine specifications
    DISPLACEMENT_L = 1.352       # Liters
    RATED_POWER_HP = 115.0       # Horsepower @ 5800 RPM
    CRITICAL_ALT_FT = 15000.0    # Turbocharger critical altitude
    NOMINAL_BSFC = 0.285         # kg / (kW * h) Brake Specific Fuel Consumption
    FUEL_DENSITY_KG_L = 0.73     # Avgas 100LL / Mogas density kg/L
    FUEL_LHV_MJ_KG = 43.5        # Lower Heating Value of Aviation Gasoline (MJ/kg)

    @classmethod
    def calculate_expected_states(
        cls,
        throttle: float,
        rpm: float,
        altitude: float,
        ambient_temp: float,
        humidity: float = 40.0
    ) -> Dict[str, float]:
        """
        Derive first-principles expected states for an aero-piston engine.
        Returns expected EGT, CHT, Fuel Flow, Thermal Stress, Engine Efficiency, and Power.
        """
        # 1. Atmospheric conditions
        isa = AtmosphereModel.get_isa_conditions(altitude, sea_level_temp_c=15.0)
        sigma = isa["density_ratio_sigma"]  # Air density ratio

        # 2. Turbocharger Boost & Manifold Absolute Pressure (MAP)
        # Wastegate maintains sea-level MAP (up to 40 inHg) below critical altitude.
        # Above critical altitude, turbo compressor reaches pressure ratio limit.
        if altitude <= cls.CRITICAL_ALT_FT:
            turbo_boost_ratio = 1.0
        else:
            excess_alt = altitude - cls.CRITICAL_ALT_FT
            turbo_boost_ratio = max(0.65, 1.0 - (excess_alt / 15000.0) * 0.35)

        # Effective volumetric air charge ratio
        effective_air_charge = (throttle / 100.0) * turbo_boost_ratio

        # 3. Estimated Brake Horsepower (BHP)
        rpm_ratio = max(0.2, min(1.2, rpm / 5800.0))
        bhp = cls.RATED_POWER_HP * (throttle / 100.0) * (0.3 + 0.7 * rpm_ratio) * turbo_boost_ratio
        bhp = max(5.0, min(120.0, bhp))
        power_kw = bhp * 0.7457

        # 4. Expected Fuel Flow (L/h)
        # Power (kW) * BSFC (kg/kWh) / density (kg/L)
        # BSFC has a slight 'U-curve' with load: highest efficiency at 65-75% throttle
        throttle_frac = max(0.05, throttle / 100.0)
        bsfc_modifier = 1.0 + 0.15 * math.pow(throttle_frac - 0.70, 2)
        fuel_mass_flow_kg_h = power_kw * (cls.NOMINAL_BSFC * bsfc_modifier)
        expected_fuel_flow = fuel_mass_flow_kg_h / cls.FUEL_DENSITY_KG_L
        # Add baseline idle fuel consumption
        expected_fuel_flow = max(2.5, expected_fuel_flow)

        # 5. Expected Exhaust Gas Temperature (EGT in °C)
        # Driven by equivalence ratio: leanest at 70-75% throttle, richer at idle and full throttle
        if throttle < 25.0:
            expected_egt = 500.0 + (throttle / 25.0) * 140.0
        elif throttle <= 78.0:
            # Lean cruise / economy zone: highest combustion temperatures
            expected_egt = 640.0 + ((throttle - 25.0) / 53.0) * 135.0  # up to 775°C
        else:
            # Full throttle enrichment (cooling effect of extra fuel)
            expected_egt = 775.0 - ((throttle - 78.0) / 22.0) * 25.0   # ~750°C

        # Altitude / backpressure adjustment: lower ambient pressure increases expansion ratio
        expected_egt -= (altitude / 1000.0) * 1.2
        # Ambient temperature bias
        expected_egt += (ambient_temp - 15.0) * 0.4

        # 6. Expected Cylinder Head Temperature (CHT in °C)
        # Balance between combustion heat rejection to cylinder walls and cooling airflow
        # Ram-air / radiator cooling effectiveness scales with air density sigma
        cooling_capacity = max(0.55, math.sqrt(sigma))
        effective_ambient = ambient_temp - (altitude / 1000.0) * 1.98

        heat_flux_to_head = 45.0 + (power_kw / 85.0) * 95.0
        expected_cht = effective_ambient + (heat_flux_to_head / cooling_capacity)
        expected_cht = max(55.0, min(240.0, expected_cht))

        # 7. Expected Oil Pressure (PSI) & Oil Temperature (°C)
        expected_oil_temp = 60.0 + (power_kw / 85.0) * 35.0 + (ambient_temp * 0.25)
        viscosity_eff = max(0.65, 1.0 - (expected_oil_temp - 75.0) * 0.0035)
        expected_oil_press = 25.0 + (rpm / 5800.0) * 45.0 * viscosity_eff

        # 8. Expected Thermal Stress Index (MPa equivalent, 0 - 100 scale)
        # Proportional to temperature gradient across cylinder wall (CHT - Ambient)
        delta_t = max(10.0, expected_cht - effective_ambient)
        expected_thermal_stress = min(100.0, (delta_t / 200.0) * 80.0)

        # 9. Expected Engine Efficiency (%)
        # Thermal efficiency = Work Output (kW) / Heat Input Rate (kW)
        fuel_energy_rate_kw = (fuel_mass_flow_kg_h / 3600.0) * (cls.FUEL_LHV_MJ_KG * 1000.0)
        efficiency_pct = (power_kw / max(1.0, fuel_energy_rate_kw)) * 100.0
        efficiency_pct = max(18.0, min(38.0, efficiency_pct))

        return {
            "expected_egt": round(expected_egt, 1),
            "expected_cht": round(expected_cht, 1),
            "expected_fuel_flow": round(expected_fuel_flow, 2),
            "expected_oil_temp": round(expected_oil_temp, 1),
            "expected_oil_press": round(expected_oil_press, 1),
            "expected_thermal_stress": round(expected_thermal_stress, 1),
            "expected_efficiency": round(efficiency_pct, 1),
            "expected_power_hp": round(bhp, 1),
            "air_density_sigma": round(sigma, 4)
        }
