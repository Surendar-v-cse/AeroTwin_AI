import React, { useState } from 'react';
import { Flame, Wrench, Droplets, Zap, Gauge, Wind, AlertCircle, CheckCircle2 } from 'lucide-react';
import { UnifiedTwinState } from '../types';

interface DigitalTwinViewProps {
  twinState: UnifiedTwinState | null;
}

export const DigitalTwinView: React.FC<DigitalTwinViewProps> = ({ twinState }) => {
  const [activeTab, setActiveTab] = useState<'schematic' | 'thermal' | 'mechanical' | 'combustion' | 'lubrication' | 'fuel'>('schematic');

  if (!twinState) return null;

  const { telemetry, subsystems, residuals } = twinState;
  const { thermal_state, mechanical_state, combustion_state, lubrication_state, fuel_state } = subsystems;

  // Derive dynamic color for cylinder heads based on CHT
  const getChtColor = (cht: number) => {
    if (cht > 230) return '#FF3355'; // Critical crimson
    if (cht > 190) return '#FFB300'; // Warning amber
    if (cht > 120) return '#00E676'; // Nominal emerald
    return '#00E5FF'; // Cool cyan
  };

  const headColor = getChtColor(telemetry.cht);

  // Status badge helper
  const renderStatusBadge = (status: string) => {
    const isNom = status === 'Nominal';
    const isWarn = status === 'Warning';
    return (
      <span
        className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold flex items-center gap-1 ${
          isNom
            ? 'text-tactical-emerald border-tactical-emerald/30 bg-tactical-emerald/10'
            : isWarn
            ? 'text-tactical-amber border-tactical-amber/30 bg-tactical-amber/10'
            : 'text-tactical-red border-tactical-red/30 bg-tactical-red/10 animate-pulse'
        }`}
      >
        {isNom ? <CheckCircle2 className="w-2.5 h-2.5" /> : <AlertCircle className="w-2.5 h-2.5" />}
        {status}
      </span>
    );
  };

  return (
    <div className="aerospace-panel p-4 mb-4 border-space-700/80">
      {/* Header with Navigation Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-space-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded bg-tactical-cyan animate-pulse" />
          <h2 className="text-sm font-bold font-mono tracking-wider uppercase text-white flex items-center gap-2">
            DIGITAL TWIN VIRTUAL ENGINE SYNCHRONIZER
            <span className="text-xs text-tactical-cyan font-normal">
              (ROTAX 914 BOXER-4 TURBOCHARGED)
            </span>
          </h2>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center gap-1 bg-space-900/80 p-1 rounded-lg border border-space-750 text-xs font-mono">
          <button
            onClick={() => setActiveTab('schematic')}
            className={`px-3 py-1 rounded transition ${
              activeTab === 'schematic' ? 'bg-tactical-cyan text-space-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            VIRTUAL SCHEMATIC
          </button>
          <button
            onClick={() => setActiveTab('thermal')}
            className={`px-3 py-1 rounded transition ${
              activeTab === 'thermal' ? 'bg-tactical-cyan text-space-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            THERMAL
          </button>
          <button
            onClick={() => setActiveTab('mechanical')}
            className={`px-3 py-1 rounded transition ${
              activeTab === 'mechanical' ? 'bg-tactical-cyan text-space-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            MECHANICAL
          </button>
          <button
            onClick={() => setActiveTab('combustion')}
            className={`px-3 py-1 rounded transition ${
              activeTab === 'combustion' ? 'bg-tactical-cyan text-space-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            COMBUSTION
          </button>
          <button
            onClick={() => setActiveTab('lubrication')}
            className={`px-3 py-1 rounded transition ${
              activeTab === 'lubrication' ? 'bg-tactical-cyan text-space-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            LUBRICATION
          </button>
          <button
            onClick={() => setActiveTab('fuel')}
            className={`px-3 py-1 rounded transition ${
              activeTab === 'fuel' ? 'bg-tactical-cyan text-space-950 font-bold' : 'text-slate-400 hover:text-white'
            }`}
          >
            FUEL SYSTEM
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {activeTab === 'schematic' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
          {/* Left: Engine SVG Interactive Cross-Section */}
          <div className="lg:col-span-8 bg-space-950/70 p-4 rounded-lg border border-space-800 relative flex items-center justify-center min-h-[300px] overflow-hidden">
            {/* Background Blueprint Grid */}
            <div className="absolute inset-0 opacity-20 pointer-events-none bg-[radial-gradient(#00E5FF_1px,transparent_1px)] [background-size:16px_16px]" />

            <svg viewBox="0 0 700 360" className="w-full max-w-2xl h-auto relative z-10">
              {/* Definitions for Glow Gradients */}
              <defs>
                <linearGradient id="exhaustGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#FF3355" stopOpacity="0.9" />
                  <stop offset="100%" stopColor="#FFB300" stopOpacity="0.4" />
                </linearGradient>
                <linearGradient id="coolantGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#00E5FF" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#3B82F6" stopOpacity="0.3" />
                </linearGradient>
                <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="4" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* Central Crankcase Block */}
              <rect
                x="260"
                y="110"
                width="180"
                height="140"
                rx="10"
                fill="#0C152B"
                stroke="#1C315E"
                strokeWidth="2.5"
              />
              <text x="350" y="145" textAnchor="middle" fill="#94A3B8" fontSize="11" fontFamily="monospace" fontWeight="bold">
                CRANKCASE / REDUCTION
              </text>
              <text x="350" y="165" textAnchor="middle" fill="#00E5FF" fontSize="13" fontFamily="monospace" fontWeight="bold">
                {Math.round(telemetry.rpm)} RPM
              </text>
              <text x="350" y="182" textAnchor="middle" fill="#64748B" fontSize="10" fontFamily="monospace">
                TORQUE: {mechanical_state.torque_nm} Nm
              </text>

              {/* Crankshaft Center Indicator */}
              <circle cx="350" cy="210" r="18" fill="#111E3A" stroke="#00E5FF" strokeWidth="2" />
              <line x1="350" y1="195" x2="350" y2="225" stroke="#00E5FF" strokeWidth="3" className="animate-spin-slow origin-[350px_210px]" />

              {/* Cylinder 1 (Top Left) */}
              <g>
                <rect x="130" y="90" width="130" height="55" rx="6" fill="#101E3A" stroke="#1C315E" strokeWidth="2" />
                {/* Cylinder Head cap with heat color */}
                <rect
                  x="100"
                  y="86"
                  width="30"
                  height="63"
                  rx="4"
                  fill={headColor}
                  filter="url(#glowFilter)"
                  opacity="0.85"
                />
                <text x="175" y="122" textAnchor="middle" fill="#E2E8F0" fontSize="11" fontFamily="monospace">
                  CYL #1: {Math.round(telemetry.cht)}°C
                </text>
              </g>

              {/* Cylinder 3 (Bottom Left) */}
              <g>
                <rect x="130" y="215" width="130" height="55" rx="6" fill="#101E3A" stroke="#1C315E" strokeWidth="2" />
                <rect
                  x="100"
                  y="211"
                  width="30"
                  height="63"
                  rx="4"
                  fill={headColor}
                  filter="url(#glowFilter)"
                  opacity="0.85"
                />
                <text x="175" y="247" textAnchor="middle" fill="#E2E8F0" fontSize="11" fontFamily="monospace">
                  CYL #3: {Math.round(telemetry.cht - 2)}°C
                </text>
              </g>

              {/* Cylinder 2 (Top Right) */}
              <g>
                <rect x="440" y="90" width="130" height="55" rx="6" fill="#101E3A" stroke="#1C315E" strokeWidth="2" />
                <rect
                  x="570"
                  y="86"
                  width="30"
                  height="63"
                  rx="4"
                  fill={headColor}
                  filter="url(#glowFilter)"
                  opacity="0.85"
                />
                <text x="505" y="122" textAnchor="middle" fill="#E2E8F0" fontSize="11" fontFamily="monospace">
                  CYL #2: {Math.round(telemetry.cht + 1)}°C
                </text>
              </g>

              {/* Cylinder 4 (Bottom Right) */}
              <g>
                <rect x="440" y="215" width="130" height="55" rx="6" fill="#101E3A" stroke="#1C315E" strokeWidth="2" />
                <rect
                  x="570"
                  y="211"
                  width="30"
                  height="63"
                  rx="4"
                  fill={headColor}
                  filter="url(#glowFilter)"
                  opacity="0.85"
                />
                <text x="505" y="247" textAnchor="middle" fill="#E2E8F0" fontSize="11" fontFamily="monospace">
                  CYL #4: {Math.round(telemetry.cht - 1)}°C
                </text>
              </g>

              {/* Turbocharger Housing (Top Center) */}
              <g>
                <rect x="300" y="25" width="100" height="50" rx="8" fill="#111E3A" stroke="#00E5FF" strokeWidth="2" />
                <circle cx="350" cy="50" r="16" fill="#080E1E" stroke="#FFB300" strokeWidth="2" className="animate-spin-slow origin-[350px_50px]" />
                <text x="350" y="42" textAnchor="middle" fill="#00E5FF" fontSize="9" fontFamily="monospace" fontWeight="bold">
                  TURBOCHARGER
                </text>
                <text x="350" y="65" textAnchor="middle" fill="#FFB300" fontSize="9" fontFamily="monospace">
                  WASTEGATE ACTIVE
                </text>
              </g>

              {/* Exhaust Manifold (Collector Pipes) */}
              <path
                d="M 100 117 L 70 117 L 70 310 L 350 310"
                fill="none"
                stroke="url(#exhaustGrad)"
                strokeWidth="4"
                strokeDasharray="6 3"
              />
              <path
                d="M 600 117 L 630 117 L 630 310 L 350 310"
                fill="none"
                stroke="url(#exhaustGrad)"
                strokeWidth="4"
                strokeDasharray="6 3"
              />
              {/* Exhaust Exit Pipe with EGT Readout */}
              <rect x="300" y="295" width="100" height="30" rx="6" fill="#111E3A" stroke="#FF3355" strokeWidth="2" />
              <text x="350" y="315" textAnchor="middle" fill="#FFB300" fontSize="11" fontFamily="monospace" fontWeight="bold">
                EGT: {Math.round(telemetry.egt)}°C
              </text>

              {/* Oil circuit indicator path */}
              <path
                d="M 270 230 L 220 290 L 480 290 L 430 230"
                fill="none"
                stroke="#00E5FF"
                strokeWidth="2"
                strokeDasharray="4 2"
                opacity="0.7"
              />
              <text x="350" y="282" textAnchor="middle" fill="#00E5FF" fontSize="9" fontFamily="monospace">
                OIL: {telemetry.oil_press} PSI | {telemetry.oil_temp}°C
              </text>
            </svg>
          </div>

          {/* Right: Quick Subsystem Telemetry Summaries */}
          <div className="lg:col-span-4 flex flex-col gap-2.5">
            {/* Thermal Mini Card */}
            <div className="bg-space-900/90 p-3 rounded-lg border border-space-750 hover:border-tactical-cyan/40 transition">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5">
                  <Flame className="w-3.5 h-3.5 text-orange-400" />
                  THERMAL STATE
                </span>
                {renderStatusBadge(thermal_state.status)}
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono mt-2 text-slate-400">
                <div>CHT Reserve: <strong className="text-slate-200">{thermal_state.cht_margin_c}°C</strong></div>
                <div>Cooling Reserve: <strong className="text-slate-200">{thermal_state.cooling_reserve_pct}%</strong></div>
                <div>Heat Flux: <strong className="text-slate-200">{thermal_state.heat_flux_kw} kW</strong></div>
                <div>Stress Idx: <strong className="text-slate-200">{thermal_state.thermal_stress_index}</strong></div>
              </div>
            </div>

            {/* Mechanical Mini Card */}
            <div className="bg-space-900/90 p-3 rounded-lg border border-space-750 hover:border-tactical-cyan/40 transition">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5">
                  <Gauge className="w-3.5 h-3.5 text-tactical-cyan" />
                  MECHANICAL STATE
                </span>
                {renderStatusBadge(mechanical_state.status)}
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono mt-2 text-slate-400">
                <div>Brake HP: <strong className="text-slate-200">{mechanical_state.power_output_hp} HP</strong></div>
                <div>Torque: <strong className="text-slate-200">{mechanical_state.torque_nm} Nm</strong></div>
                <div>Mech Stress: <strong className="text-slate-200">{mechanical_state.mechanical_stress_index}</strong></div>
                <div>Vibe Risk: <strong className="text-slate-200">{mechanical_state.vibration_risk_index}</strong></div>
              </div>
            </div>

            {/* Combustion Mini Card */}
            <div className="bg-space-900/90 p-3 rounded-lg border border-space-750 hover:border-tactical-cyan/40 transition">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-yellow-400" />
                  COMBUSTION STATE
                </span>
                {renderStatusBadge(combustion_state.status)}
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono mt-2 text-slate-400">
                <div>Lambda λ: <strong className="text-slate-200">{combustion_state.lambda_ratio}</strong></div>
                <div>AFR: <strong className="text-slate-200">{combustion_state.estimated_afr}:1</strong></div>
                <div>Quality: <strong className="text-slate-200">{combustion_state.combustion_quality_score}%</strong></div>
                <div>Detonation Risk: <strong className="text-slate-200">{combustion_state.detonation_risk_index}</strong></div>
              </div>
            </div>

            {/* Lubrication Mini Card */}
            <div className="bg-space-900/90 p-3 rounded-lg border border-space-750 hover:border-tactical-cyan/40 transition">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-mono font-semibold text-slate-300 flex items-center gap-1.5">
                  <Droplets className="w-3.5 h-3.5 text-blue-400" />
                  LUBRICATION STATE
                </span>
                {renderStatusBadge(lubrication_state.status)}
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono mt-2 text-slate-400">
                <div>Viscosity: <strong className="text-slate-200">{lubrication_state.viscosity_cst} cSt</strong></div>
                <div>Film Integrity: <strong className="text-slate-200">{lubrication_state.oil_film_integrity}%</strong></div>
                <div>Degradation: <strong className="text-slate-200">{lubrication_state.lubrication_degradation_index}</strong></div>
                <div>Margin: <strong className="text-slate-200">{lubrication_state.scavenge_pressure_margin_psi} PSI</strong></div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Detailed Tab Views */
        <div className="bg-space-950/70 p-4 rounded-lg border border-space-800">
          {activeTab === 'thermal' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold font-mono text-tactical-cyan uppercase">THERMAL BALANCE & EXPANSION ENVELOPE</h3>
                {renderStatusBadge(thermal_state.status)}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">CHT Margin to Redline</div>
                  <div className="text-xl font-bold text-white mt-1">{thermal_state.cht_margin_c} °C</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">EGT Margin to Redline</div>
                  <div className="text-xl font-bold text-white mt-1">{thermal_state.egt_margin_c} °C</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Thermal Gradient (EGT - CHT)</div>
                  <div className="text-xl font-bold text-white mt-1">{thermal_state.thermal_gradient_c} °C</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Cylinder Head Heat Flux</div>
                  <div className="text-xl font-bold text-white mt-1">{thermal_state.heat_flux_kw} kW</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'mechanical' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold font-mono text-tactical-cyan uppercase">ROTATING INERTIA & MECHANICAL LOADING</h3>
                {renderStatusBadge(mechanical_state.status)}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Indicated Brake Power</div>
                  <div className="text-xl font-bold text-white mt-1">{mechanical_state.power_output_hp} HP</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Estimated Shaft Torque</div>
                  <div className="text-xl font-bold text-white mt-1">{mechanical_state.torque_nm} Nm</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Mechanical Stress Index</div>
                  <div className="text-xl font-bold text-white mt-1">{mechanical_state.mechanical_stress_index} / 100</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Vibration Risk Index</div>
                  <div className="text-xl font-bold text-white mt-1">{mechanical_state.vibration_risk_index} / 100</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'combustion' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold font-mono text-tactical-cyan uppercase">STOICHIOMETRY & DETONATION RISK</h3>
                {renderStatusBadge(combustion_state.status)}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Air-Fuel Lambda (λ)</div>
                  <div className="text-xl font-bold text-white mt-1">{combustion_state.lambda_ratio}</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Combustion Quality Score</div>
                  <div className="text-xl font-bold text-white mt-1">{combustion_state.combustion_quality_score}%</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Detonation / Knock Risk</div>
                  <div className="text-xl font-bold text-white mt-1">{combustion_state.detonation_risk_index} / 100</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Misfire Risk Probability</div>
                  <div className="text-xl font-bold text-white mt-1">{combustion_state.misfire_risk_pct}%</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'lubrication' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold font-mono text-tactical-cyan uppercase">HYDRODYNAMIC FILM & VISCOSITY ANALYSIS</h3>
                {renderStatusBadge(lubrication_state.status)}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Kinematic Viscosity (cSt)</div>
                  <div className="text-xl font-bold text-white mt-1">{lubrication_state.viscosity_cst} cSt</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Oil Film Thickness Integrity</div>
                  <div className="text-xl font-bold text-white mt-1">{lubrication_state.oil_film_integrity}%</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Thermal Degradation Index</div>
                  <div className="text-xl font-bold text-white mt-1">{lubrication_state.lubrication_degradation_index} / 100</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Scavenge Pressure Margin</div>
                  <div className="text-xl font-bold text-white mt-1">{lubrication_state.scavenge_pressure_margin_psi} PSI</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'fuel' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-bold font-mono text-tactical-cyan uppercase">FUEL INJECTION & RAIL PRESSURE</h3>
                {renderStatusBadge(fuel_state.status)}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Injector Duty Cycle</div>
                  <div className="text-xl font-bold text-white mt-1">{fuel_state.injector_duty_cycle_pct}%</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Delivery Compliance</div>
                  <div className="text-xl font-bold text-white mt-1">{fuel_state.delivery_compliance_pct}%</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Vapor Lock Risk Index</div>
                  <div className="text-xl font-bold text-white mt-1">{fuel_state.vapor_lock_risk_index} / 100</div>
                </div>
                <div className="bg-space-900 p-3 rounded border border-space-750">
                  <div className="text-slate-400">Fuel Rail Compliance</div>
                  <div className="text-xl font-bold text-white mt-1">{fuel_state.fuel_rail_pressure_margin}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
