import React, { useState } from 'react';
import { Mountain, SunMedium, Compass, AlertTriangle, RotateCcw } from 'lucide-react';
import { api } from '../services/api';

interface MissionSimulatorProps {
  onScenarioActivated?: (scenario: string) => void;
}

export const MissionSimulator: React.FC<MissionSimulatorProps> = ({ onScenarioActivated }) => {
  const [activeScenario, setActiveScenario] = useState<string>('nominal');
  const [loading, setLoading] = useState(false);

  const scenarios = [
    {
      id: 'high_altitude',
      name: 'High Altitude Mission',
      desc: '22,000 FT | Cold Ambient (-22°C) | Turbocharger Boost Limit Stress',
      icon: Mountain,
      color: 'text-cyan-400',
      border: 'border-cyan-500/40 hover:border-cyan-400',
      bg: 'hover:bg-cyan-500/10',
    },
    {
      id: 'hot_weather',
      name: 'Hot Weather Mission',
      desc: '48°C Desert Ambient | Reduced Radiator Heat Dissipation Margin',
      icon: SunMedium,
      color: 'text-amber-400',
      border: 'border-amber-500/40 hover:border-amber-400',
      bg: 'hover:bg-amber-500/10',
    },
    {
      id: 'endurance',
      name: 'Endurance Mission',
      desc: '14-Hour Loiter Profile | Max Range Cruise BSFC Optimization',
      icon: Compass,
      color: 'text-purple-400',
      border: 'border-purple-500/40 hover:border-purple-400',
      bg: 'hover:bg-purple-500/10',
    },
    {
      id: 'emergency',
      name: 'Emergency Thermal Runaway',
      desc: 'Cooling Duct Jammed | CHT Excursion > 240°C | In-Flight IFSD Risk',
      icon: AlertTriangle,
      color: 'text-rose-400',
      border: 'border-rose-500/40 hover:border-rose-400',
      bg: 'hover:bg-rose-500/10',
    },
  ];

  const handleTrigger = async (scenarioId: string) => {
    setLoading(true);
    setActiveScenario(scenarioId);
    try {
      await api.triggerScenario(scenarioId);
      onScenarioActivated?.(scenarioId);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="aerospace-panel p-4 mb-4 border-space-700/80">
      <div className="flex items-center justify-between mb-3 border-b border-space-800 pb-2">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-tactical-cyan" />
          <h2 className="text-xs font-mono font-bold text-white uppercase tracking-wider">
            MISSION PROFILE SIMULATION MODULE (RAPID SCENARIO INGESTION)
          </h2>
        </div>
        <button
          onClick={() => handleTrigger('nominal')}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono font-bold bg-space-900 hover:bg-space-800 text-tactical-emerald border border-tactical-emerald/40 transition"
        >
          <RotateCcw className="w-3 h-3" />
          RESET NOMINAL CRUISE
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {scenarios.map((sc) => {
          const Icon = sc.icon;
          const isSelected = activeScenario === sc.id;
          return (
            <button
              key={sc.id}
              onClick={() => handleTrigger(sc.id)}
              disabled={loading}
              className={`p-3 rounded-lg border text-left flex flex-col justify-between transition-all ${
                isSelected
                  ? 'bg-space-850 border-tactical-cyan shadow-hud-cyan'
                  : `bg-space-900/80 ${sc.border} ${sc.bg}`
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-xs font-mono font-bold ${sc.color}`}>
                  {sc.name}
                </span>
                <Icon className={`w-4 h-4 ${sc.color}`} />
              </div>
              <p className="text-[11px] font-mono text-slate-400 leading-relaxed">
                {sc.desc}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
