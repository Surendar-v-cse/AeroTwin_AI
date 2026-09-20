import React, { useState } from 'react';
import { Sliders, RefreshCw, AlertOctagon, CheckCircle, ShieldAlert, Cpu } from 'lucide-react';
import { UnifiedTwinState } from '../types';
import { api } from '../services/api';

interface TelemetrySimulatorProps {
  twinState: UnifiedTwinState | null;
}

export const TelemetrySimulator: React.FC<TelemetrySimulatorProps> = ({ twinState }) => {
  const [isUpdating, setIsUpdating] = useState(false);

  if (!twinState) return null;

  const { telemetry, simulation_mode, active_fault } = twinState;

  // Handle Mode Switch
  const handleModeChange = async (mode: 'manual' | 'auto') => {
    setIsUpdating(true);
    try {
      await api.setSimulatorMode(mode);
    } catch (err) {
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  // Handle Input Changes
  const handleParamChange = async (key: string, value: number | string) => {
    try {
      await api.updateTelemetry({ [key]: value });
    } catch (err) {
      console.error(err);
    }
  };

  // Handle Fault Injection
  const handleInjectFault = async (faultType: string) => {
    setIsUpdating(true);
    try {
      await api.injectFault(faultType, 1.0);
    } catch (err) {
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  const missionPhases = ['Takeoff', 'Climb', 'Cruise', 'Loiter', 'Descent', 'Landing'];

  return (
    <div className="aerospace-panel p-4 mb-4 border-space-700/80">
      {/* Panel Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 border-b border-space-800 pb-3">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-tactical-cyan" />
          <h2 className="text-xs font-mono font-bold text-white uppercase tracking-wider">
            LAYER 1: TELEMETRY SIMULATION CONTROLS & TEST HARNESS
          </h2>
        </div>

        {/* Mode Toggle A vs B */}
        <div className="flex items-center gap-2 bg-space-900 p-1 rounded-lg border border-space-750">
          <button
            onClick={() => handleModeChange('auto')}
            className={`px-3 py-1 text-xs font-mono rounded font-semibold transition flex items-center gap-1.5 ${
              simulation_mode === 'auto'
                ? 'bg-tactical-cyan text-space-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <RefreshCw className={`w-3 h-3 ${simulation_mode === 'auto' ? 'animate-spin-slow' : ''}`} />
            MODE B: AUTO (PHYSICS-COUPLED)
          </button>
          <button
            onClick={() => handleModeChange('manual')}
            className={`px-3 py-1 text-xs font-mono rounded font-semibold transition flex items-center gap-1.5 ${
              simulation_mode === 'manual'
                ? 'bg-tactical-cyan text-space-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sliders className="w-3 h-3" />
            MODE A: MANUAL CONTROL
          </button>
        </div>
      </div>

      {/* Primary Flight Controls: Throttle, Altitude, Ambient, Humidity, Phase */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 bg-space-950/60 p-3.5 rounded-lg border border-space-800 mb-4">
        {/* Mission Phase Dropdown */}
        <div className="flex flex-col gap-1.5">
          <label className="text-[11px] font-mono text-slate-400 font-semibold uppercase">
            MISSION PHASE
          </label>
          <select
            value={telemetry.mission_phase}
            onChange={(e) => handleParamChange('mission_phase', e.target.value)}
            className="bg-space-900 text-tactical-cyan text-xs font-mono p-2 rounded border border-space-700 focus:outline-none focus:border-tactical-cyan"
          >
            {missionPhases.map((phase) => (
              <option key={phase} value={phase}>
                {phase}
              </option>
            ))}
          </select>
          <span className="text-[10px] text-slate-500 font-mono">
            Auto-tunes flight profiles
          </span>
        </div>

        {/* Throttle Position Slider */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between text-[11px] font-mono text-slate-400">
            <span className="font-semibold uppercase">THROTTLE</span>
            <span className="text-tactical-cyan font-bold">{Math.round(telemetry.throttle)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={telemetry.throttle}
            onChange={(e) => handleParamChange('throttle', parseFloat(e.target.value))}
            className="w-full cursor-pointer"
          />
          <span className="text-[10px] text-slate-500 font-mono">
            Drives RPM, EGT, Fuel Flow
          </span>
        </div>

        {/* Altitude Slider */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between text-[11px] font-mono text-slate-400">
            <span className="font-semibold uppercase">ALTITUDE</span>
            <span className="text-tactical-cyan font-bold">{Math.round(telemetry.altitude).toLocaleString()} FT</span>
          </div>
          <input
            type="range"
            min="0"
            max="25000"
            step="250"
            value={telemetry.altitude}
            onChange={(e) => handleParamChange('altitude', parseFloat(e.target.value))}
            className="w-full cursor-pointer"
          />
          <span className="text-[10px] text-slate-500 font-mono">
            Air density drop (ISA Model)
          </span>
        </div>

        {/* Ambient Temperature Slider */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between text-[11px] font-mono text-slate-400">
            <span className="font-semibold uppercase">AMBIENT TEMP</span>
            <span className="text-tactical-cyan font-bold">{Math.round(telemetry.ambient_temp)} °C</span>
          </div>
          <input
            type="range"
            min="-20"
            max="60"
            step="1"
            value={telemetry.ambient_temp}
            onChange={(e) => handleParamChange('ambient_temp', parseFloat(e.target.value))}
            className="w-full cursor-pointer"
          />
          <span className="text-[10px] text-slate-500 font-mono">
            Directly impacts CHT cooling
          </span>
        </div>

        {/* Humidity Slider */}
        <div className="flex flex-col gap-1.5">
          <div className="flex justify-between text-[11px] font-mono text-slate-400">
            <span className="font-semibold uppercase">HUMIDITY</span>
            <span className="text-tactical-cyan font-bold">{Math.round(telemetry.humidity)}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            step="5"
            value={telemetry.humidity}
            onChange={(e) => handleParamChange('humidity', parseFloat(e.target.value))}
            className="w-full cursor-pointer"
          />
          <span className="text-[10px] text-slate-500 font-mono">
            Atmospheric air density factor
          </span>
        </div>
      </div>

      {/* Manual Mode Direct Sliders: Enabled only in Mode A */}
      {simulation_mode === 'manual' && (
        <div className="bg-space-950/40 p-3.5 rounded-lg border border-dashed border-tactical-cyan/40 mb-4 animate-fadeIn">
          <div className="text-xs font-mono font-bold text-tactical-cyan uppercase mb-3 flex items-center gap-2">
            <span>MODE A DIRECT SENSOR OVERRIDES (UNCOUPLED MANUAL SLIDERS)</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {/* RPM */}
            <div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                <span>RPM</span>
                <span className="text-white font-bold">{Math.round(telemetry.rpm)}</span>
              </div>
              <input
                type="range"
                min="1000"
                max="7000"
                step="50"
                value={telemetry.rpm}
                onChange={(e) => handleParamChange('rpm', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* EGT */}
            <div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                <span>EGT (°C)</span>
                <span className="text-white font-bold">{Math.round(telemetry.egt)}</span>
              </div>
              <input
                type="range"
                min="300"
                max="900"
                step="5"
                value={telemetry.egt}
                onChange={(e) => handleParamChange('egt', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* CHT */}
            <div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                <span>CHT (°C)</span>
                <span className="text-white font-bold">{Math.round(telemetry.cht)}</span>
              </div>
              <input
                type="range"
                min="50"
                max="300"
                step="2"
                value={telemetry.cht}
                onChange={(e) => handleParamChange('cht', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Oil Temp */}
            <div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                <span>Oil Temp (°C)</span>
                <span className="text-white font-bold">{Math.round(telemetry.oil_temp)}</span>
              </div>
              <input
                type="range"
                min="20"
                max="150"
                step="1"
                value={telemetry.oil_temp}
                onChange={(e) => handleParamChange('oil_temp', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Oil Press */}
            <div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                <span>Oil Press (PSI)</span>
                <span className="text-white font-bold">{Math.round(telemetry.oil_press)}</span>
              </div>
              <input
                type="range"
                min="10"
                max="120"
                step="1"
                value={telemetry.oil_press}
                onChange={(e) => handleParamChange('oil_press', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Fuel Flow */}
            <div>
              <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
                <span>Fuel Flow (L/h)</span>
                <span className="text-white font-bold">{telemetry.fuel_flow.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="60"
                step="0.5"
                value={telemetry.fuel_flow}
                onChange={(e) => handleParamChange('fuel_flow', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
        </div>
      )}

      {/* Fault Injection Harness */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-space-800">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-tactical-amber" />
          <span className="text-xs font-mono font-bold text-slate-300 uppercase">
            PHYSICAL FAULT INJECTION HARNESS:
          </span>
          {active_fault && active_fault !== 'none' && (
            <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-tactical-red/20 text-tactical-red border border-tactical-red/40 animate-pulse">
              ACTIVE FAULT: {active_fault.toUpperCase()}
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => handleInjectFault('injector_clog')}
            className={`px-2.5 py-1 text-xs font-mono rounded border transition ${
              active_fault === 'injector_clog'
                ? 'bg-tactical-red text-white border-tactical-red'
                : 'bg-space-900 text-slate-300 border-space-700 hover:border-tactical-red/60'
            }`}
          >
            INJECTOR CLOG
          </button>

          <button
            onClick={() => handleInjectFault('oil_leak')}
            className={`px-2.5 py-1 text-xs font-mono rounded border transition ${
              active_fault === 'oil_leak'
                ? 'bg-tactical-red text-white border-tactical-red'
                : 'bg-space-900 text-slate-300 border-space-700 hover:border-tactical-red/60'
            }`}
          >
            OIL LEAK
          </button>

          <button
            onClick={() => handleInjectFault('cooling_duct_blockage')}
            className={`px-2.5 py-1 text-xs font-mono rounded border transition ${
              active_fault === 'cooling_duct_blockage'
                ? 'bg-tactical-red text-white border-tactical-red'
                : 'bg-space-900 text-slate-300 border-space-700 hover:border-tactical-red/60'
            }`}
          >
            COOLING BLOCKAGE
          </button>

          <button
            onClick={() => handleInjectFault('sensor_drift')}
            className={`px-2.5 py-1 text-xs font-mono rounded border transition ${
              active_fault === 'sensor_drift'
                ? 'bg-tactical-amber text-space-950 border-tactical-amber font-bold'
                : 'bg-space-900 text-slate-300 border-space-700 hover:border-tactical-amber/60'
            }`}
          >
            SENSOR DRIFT
          </button>

          <button
            onClick={() => handleInjectFault('none')}
            className="px-3 py-1 text-xs font-mono rounded bg-space-800 text-tactical-emerald hover:bg-tactical-emerald/20 border border-tactical-emerald/40 transition font-bold"
          >
            RESTORE NOMINAL
          </button>
        </div>
      </div>
    </div>
  );
};
