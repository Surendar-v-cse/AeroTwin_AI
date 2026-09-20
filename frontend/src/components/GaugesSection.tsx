import React from 'react';
import { GaugeDial } from './GaugeDial';
import { UnifiedTwinState } from '../types';

interface GaugesSectionProps {
  twinState: UnifiedTwinState | null;
}

export const GaugesSection: React.FC<GaugesSectionProps> = ({ twinState }) => {
  if (!twinState) return null;

  const { telemetry, expected_state } = twinState;

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <span className="w-2 h-2 rounded bg-tactical-cyan" />
          CORE TELEMETRY GAUGES MATRIX (PHYSICS-SYNCHRONIZED)
        </div>
        <div className="text-[11px] font-mono text-slate-400 flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-tactical-cyan inline-block" />
            CYAN NOTCH = DIGITAL TWIN EXPECTED
          </span>
          <span className="text-slate-600">|</span>
          <span className="flex items-center gap-1 text-slate-400">
            SOLID ARC = LIVE SENSOR
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
        {/* 1. RPM */}
        <GaugeDial
          label="Engine Speed"
          value={telemetry.rpm}
          expectedValue={expected_state?.expected_power_hp ? 5088 : undefined}
          min={1000}
          max={7000}
          unit="RPM"
          decimals={0}
          zones={{
            nominal: [4500, 5800],
            warning: [5800, 6400],
            critical: [6400, 7000],
          }}
        />

        {/* 2. EGT */}
        <GaugeDial
          label="Exhaust Gas Temp"
          value={telemetry.egt}
          expectedValue={expected_state?.expected_egt}
          min={300}
          max={900}
          unit="°C"
          decimals={1}
          zones={{
            nominal: [650, 800],
            warning: [800, 850],
            critical: [850, 900],
          }}
        />

        {/* 3. CHT */}
        <GaugeDial
          label="Cylinder Head Temp"
          value={telemetry.cht}
          expectedValue={expected_state?.expected_cht}
          min={50}
          max={300}
          unit="°C"
          decimals={1}
          zones={{
            nominal: [100, 180],
            warning: [180, 220],
            critical: [220, 300],
          }}
        />

        {/* 4. Oil Temp */}
        <GaugeDial
          label="Oil Temperature"
          value={telemetry.oil_temp}
          expectedValue={expected_state?.expected_oil_temp}
          min={20}
          max={150}
          unit="°C"
          decimals={1}
          zones={{
            nominal: [70, 105],
            warning: [105, 125],
            critical: [125, 150],
          }}
        />

        {/* 5. Oil Pressure */}
        <GaugeDial
          label="Oil Pressure"
          value={telemetry.oil_press}
          expectedValue={expected_state?.expected_oil_press}
          min={10}
          max={120}
          unit="PSI"
          decimals={1}
          zones={{
            nominal: [45, 80],
            warning: [30, 45],
            critical: [10, 30],
          }}
        />

        {/* 6. Fuel Flow */}
        <GaugeDial
          label="Fuel Flow"
          value={telemetry.fuel_flow}
          expectedValue={expected_state?.expected_fuel_flow}
          min={0}
          max={60}
          unit="L/H"
          decimals={1}
          zones={{
            nominal: [10, 32],
            warning: [32, 45],
            critical: [45, 60],
          }}
        />
      </div>
    </div>
  );
};
