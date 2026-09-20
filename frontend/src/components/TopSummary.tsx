import React from 'react';
import { Activity, ShieldAlert, Clock, AlertTriangle, CheckCircle2, Flame } from 'lucide-react';
import { UnifiedTwinState } from '../types';

interface TopSummaryProps {
  twinState: UnifiedTwinState | null;
}

export const TopSummary: React.FC<TopSummaryProps> = ({ twinState }) => {
  if (!twinState) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="aerospace-panel p-4 animate-pulse h-28 bg-space-850" />
        ))}
      </div>
    );
  }

  const { health, readiness, rul, anomaly, faults } = twinState;

  // Health color mapping
  const healthColor =
    health.health_category === 'Excellent'
      ? 'text-tactical-emerald'
      : health.health_category === 'Good'
      ? 'text-tactical-cyan'
      : health.health_category === 'Warning'
      ? 'text-tactical-amber'
      : 'text-tactical-red';

  const healthBorder =
    health.health_category === 'Excellent'
      ? 'border-tactical-emerald/30 shadow-hud-emerald'
      : health.health_category === 'Good'
      ? 'border-tactical-cyan/30 shadow-hud-cyan'
      : health.health_category === 'Warning'
      ? 'border-tactical-amber/30 shadow-hud-amber'
      : 'border-tactical-red/40 shadow-hud-red';

  // Risk Level determination
  const riskLevel =
    health.health_score < 60 || faults.is_critical
      ? { label: 'CRITICAL', color: 'text-tactical-red', bg: 'bg-tactical-red/10', border: 'border-tactical-red/40' }
      : health.health_score < 75 || anomaly.anomaly_status === 'Warning'
      ? { label: 'ELEVATED', color: 'text-tactical-amber', bg: 'bg-tactical-amber/10', border: 'border-tactical-amber/40' }
      : health.health_score < 88
      ? { label: 'MODERATE', color: 'text-tactical-cyan', bg: 'bg-tactical-cyan/10', border: 'border-tactical-cyan/40' }
      : { label: 'LOW RISK', color: 'text-tactical-emerald', bg: 'bg-tactical-emerald/10', border: 'border-tactical-emerald/40' };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-4">
      {/* 1. HEALTH SCORE */}
      <div className={`aerospace-panel p-4 ${healthBorder} transition-all duration-300 relative overflow-hidden`}>
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono mb-1">
          <span className="flex items-center gap-1.5 font-semibold uppercase tracking-wider">
            <Activity className={`w-4 h-4 ${healthColor}`} />
            PROPULSION HEALTH
          </span>
          <span className={`text-[11px] font-bold uppercase px-1.5 py-0.2 rounded border border-current ${healthColor}`}>
            {health.health_category}
          </span>
        </div>
        <div className="flex items-baseline justify-between mt-2">
          <div className="flex items-baseline gap-1">
            <span className={`text-4xl font-black font-mono tracking-tight ${healthColor}`}>
              {health.health_score}
            </span>
            <span className="text-xs font-mono text-slate-400">/ 100</span>
          </div>
          <div className="text-right text-[11px] font-mono text-slate-400">
            <div>Deductions: <span className="text-slate-200">-{Math.round(100 - health.health_score)} pts</span></div>
            <div className="text-[10px] text-slate-500">
              Anomaly: -{health.deductions.anomaly_deduction} | Physics: -{health.deductions.physics_residual_deduction}
            </div>
          </div>
        </div>
        {/* Progress Bar */}
        <div className="w-full bg-space-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              health.health_category === 'Excellent'
                ? 'bg-tactical-emerald'
                : health.health_category === 'Good'
                ? 'bg-tactical-cyan'
                : health.health_category === 'Warning'
                ? 'bg-tactical-amber'
                : 'bg-tactical-red'
            }`}
            style={{ width: `${Math.max(5, health.health_score)}%` }}
          />
        </div>
      </div>

      {/* 2. MISSION READINESS */}
      <div className="aerospace-panel p-4 border-space-700/80 transition-all duration-300">
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono mb-1">
          <span className="flex items-center gap-1.5 font-semibold uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4 text-tactical-cyan" />
            MISSION READINESS
          </span>
          <span className="text-[11px] font-mono text-slate-400">
            AUTH: <strong className={readiness.flight_authorized ? 'text-tactical-emerald' : 'text-tactical-red'}>
              {readiness.flight_authorized ? 'CLEARED' : 'GROUNDED'}
            </strong>
          </span>
        </div>
        <div className="mt-2">
          <div className="text-xl font-bold font-mono tracking-tight text-white flex items-center gap-2">
            {readiness.mission_readiness}
          </div>
          <p className="text-xs text-slate-400 mt-1 line-clamp-2">
            {readiness.description}
          </p>
        </div>
      </div>

      {/* 3. FLIGHT RISK LEVEL */}
      <div className="aerospace-panel p-4 border-space-700/80 transition-all duration-300">
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono mb-1">
          <span className="flex items-center gap-1.5 font-semibold uppercase tracking-wider">
            <ShieldAlert className={`w-4 h-4 ${riskLevel.color}`} />
            TACTICAL RISK LEVEL
          </span>
          <span className={`text-[11px] font-mono font-bold px-1.5 py-0.5 rounded border ${riskLevel.color} ${riskLevel.border} ${riskLevel.bg}`}>
            {riskLevel.label}
          </span>
        </div>
        <div className="flex items-baseline justify-between mt-2">
          <div>
            <div className="text-xs text-slate-400 font-mono">50-HR IFSD RISK:</div>
            <div className={`text-2xl font-bold font-mono ${riskLevel.color}`}>
              {rul.failure_probability_50h_pct}%
            </div>
          </div>
          <div className="text-right text-xs font-mono text-slate-400">
            <div>Fault: <strong className="text-slate-200">{faults.predicted_fault}</strong></div>
            <div className="text-[11px] text-slate-500">Confidence: {faults.confidence_pct}%</div>
          </div>
        </div>
      </div>

      {/* 4. REMAINING USEFUL LIFE (RUL) */}
      <div className="aerospace-panel p-4 border-space-700/80 transition-all duration-300">
        <div className="flex items-center justify-between text-xs text-slate-400 font-mono mb-1">
          <span className="flex items-center gap-1.5 font-semibold uppercase tracking-wider">
            <Clock className="w-4 h-4 text-tactical-purple" />
            REMAINING USEFUL LIFE
          </span>
          <span className="text-[11px] font-mono text-tactical-purple font-semibold">
            TBO: {rul.nominal_tbo_hours}H
          </span>
        </div>
        <div className="flex items-baseline justify-between mt-2">
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-black font-mono text-slate-100">
              {rul.hours_remaining}
            </span>
            <span className="text-xs font-mono text-slate-400">HOURS</span>
          </div>
          <div className="text-right text-[11px] font-mono text-slate-400">
            <div>Engine Health: <strong className="text-tactical-purple">{rul.engine_health_pct}%</strong></div>
            <div className="text-[10px] text-slate-500">Wear Multiplier: {rul.composite_wear_rate}x</div>
          </div>
        </div>
        {/* Degradation bar */}
        <div className="w-full bg-space-800 h-1.5 rounded-full mt-3 overflow-hidden">
          <div
            className="h-full bg-tactical-purple transition-all duration-500 rounded-full"
            style={{ width: `${Math.max(2, rul.engine_health_pct)}%` }}
          />
        </div>
      </div>
    </div>
  );
};
