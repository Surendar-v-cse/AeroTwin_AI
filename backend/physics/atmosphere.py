import math

class AtmosphereModel:
    """
    International Standard Atmosphere (ISA) Model for UAV altitudes up to 25,000 ft.
    Calculates ambient temperature, pressure, density ratio (sigma), and air density.
    """
    T0 = 288.15      # Sea-level standard temperature (Kelvin) = 15°C
    P0 = 101325.0    # Sea-level standard pressure (Pascals)
    RHO0 = 1.225     # Sea-level air density (kg/m^3)
    R = 287.058      # Specific gas constant for dry air (J/(kg*K))
    LAPSE_RATE_FT = 0.0019812  # Temperature lapse rate K/ft (~6.5 K/km)

    @classmethod
    def get_isa_conditions(cls, altitude_ft: float, sea_level_temp_c: float = 15.0):
        h = max(0.0, min(30000.0, altitude_ft))

        # Ambient temperature at altitude (Kelvin and Celsius)
        t_base_k = sea_level_temp_c + 273.15
        temp_k = t_base_k - cls.LAPSE_RATE_FT * h
        temp_c = temp_k - 273.15

        # Standard pressure ratio
        # P / P0 = (1 - 6.875e-6 * h)^5.25588
        base_term = max(0.1, 1.0 - 6.8753e-6 * h)
        pressure_pa = cls.P0 * math.pow(base_term, 5.25588)

        # Density from ideal gas law rho = P / (R * T)
        density = pressure_pa / (cls.R * temp_k)
        density_ratio_sigma = density / cls.RHO0

        return {
            "altitude_ft": h,
            "temperature_k": round(temp_k, 2),
            "temperature_c": round(temp_c, 2),
            "pressure_pa": round(pressure_pa, 1),
            "pressure_inhg": round(pressure_pa / 3386.389, 2),
            "density_kg_m3": round(density, 4),
            "density_ratio_sigma": round(density_ratio_sigma, 4)
        }
