import React from 'react';
import { Cpu, Zap, Thermometer, ShieldAlert, HeartPulse } from 'lucide-react';
import { VirtualSensorsData } from '../types';

interface VirtualSensorsProps {
  virtualSensors: VirtualSensorsData | null;
}

export const VirtualSensors: React.FC<VirtualSensorsProps> = ({ virtualSensors }) => {
  if (!virtualSensors) return null;

  const sensors = [
    {
      name: 'Engine Thermal Efficiency',
      value: `${virtualSensors.engine_efficiency_pct}%`,
      icon: Zap,
      color: 'text-tactical-cyan',
      borderColor: 'border-tactical-cyan/30',
      bgGlow: 'bg-tactical-cyan/10',
      status: 'Nominal Range: 28-34%',
      barValue: (virtualSensors.engine_efficiency_pct / 40.0) * 100,
    },
    {
      name: 'Cylinder Thermal Stress',
      value: `${virtualSensors.cylinder_thermal_stress_index} / 100`,
      icon: Thermometer,
      color: virtualSensors.cylinder_thermal_stress_index > 75 ? 'text-tactical-red' : virtualSensors.cylinder_thermal_stress_index > 60 ? 'text-tactical-amber' : 'text-tactical-emerald',
      borderColor: 'border-space-700',
      bgGlow: 'bg-space-900',
      status: 'Metal Temper Margin',
      barValue: virtualSensors.cylinder_thermal_stress_index,
    },
    {
      name: 'Mechanical Wear Index',
      value: `${virtualSensors.wear_index} / 100`,
      icon: ShieldAlert,
      color: virtualSensors.wear_index > 70 ? 'text-tactical-red' : 'text-tactical-purple',
      borderColor: 'border-space-700',
      bgGlow: 'bg-space-900',
      status: 'Bearing & Ring Fatigue',
      barValue: virtualSensors.wear_index,
    },
    {
      name: 'Combustion Quality Score',
      value: `${virtualSensors.combustion_quality_score}%`,
      icon: Cpu,
      color: virtualSensors.combustion_quality_score < 70 ? 'text-tactical-amber' : 'text-tactical-emerald',
      borderColor: 'border-space-700',
      bgGlow: 'bg-space-900',
      status: 'Flamefront Stability',
      barValue: virtualSensors.combustion_quality_score,
    },
    {
      name: 'Overall Twin Health Index',
      value: `${virtualSensors.overall_health_index} / 100`,
      icon: HeartPulse,
      color: virtualSensors.overall_health_index < 60 ? 'text-tactical-red' : virtualSensors.overall_health_index < 75 ? 'text-tactical-amber' : 'text-tactical-cyan',
      borderColor: 'border-space-700',
      bgGlow: 'bg-space-900',
      status: 'Multi-Physics Holistic',
      barValue: virtualSensors.overall_health_index,
    },
  ];

  return (
    <div className="aerospace-panel p-4 mb-4 border-space-700/80">
      <div className="flex items-center justify-between mb-3 border-b border-space-800 pb-2">
        <div className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Cpu className="w-4 h-4 text-tactical-cyan" />
          DIGITAL TWIN VIRTUAL SENSORS (IN-FLIGHT SYNTHESIZED)
        </div>
        <span className="text-[11px] font-mono text-tactical-emerald flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-tactical-emerald animate-ping" />
          STATE OBSERVERS ACTIVE
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {sensors.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div
              key={idx}
              className="bg-space-900/90 p-3 rounded-lg border border-space-750 flex flex-col justify-between hover:border-tactical-cyan/40 transition"
            >
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] font-mono text-slate-400 truncate">{s.name}</span>
                <Icon className={`w-3.5 h-3.5 ${s.color}`} />
              </div>
              <div>
                <div className={`text-xl font-bold font-mono ${s.color}`}>
                  {s.value}
                </div>
                <div className="w-full bg-space-800 h-1 rounded-full mt-2 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 rounded-full ${
                      s.barValue > 75 && (s.name.includes('Stress') || s.name.includes('Wear'))
                        ? 'bg-tactical-red'
                        : 'bg-tactical-cyan'
                    }`}
                    style={{ width: `${Math.min(100, Math.max(5, s.barValue))}%` }}
                  />
                </div>
              </div>
              <div className="text-[10px] font-mono text-slate-500 mt-2 truncate">
                {s.status}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
