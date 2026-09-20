import React from 'react';
import { Wrench, AlertTriangle, CheckCircle, ShieldAlert, Clock, ChevronRight } from 'lucide-react';
import { MaintenanceData } from '../types';

interface MaintenancePanelProps {
  maintenance: MaintenanceData | null;
}

export const MaintenancePanel: React.FC<MaintenancePanelProps> = ({ maintenance }) => {
  if (!maintenance) return null;

  const { active_alerts, maintenance_recommendations, urgent_pilot_actions } = maintenance;

  return (
    <div className="aerospace-panel p-4 mb-4 border-space-700/80">
      <div className="flex items-center justify-between mb-3 border-b border-space-800 pb-2">
        <div className="flex items-center gap-2">
          <Wrench className="w-4 h-4 text-tactical-cyan" />
          <h2 className="text-xs font-mono font-bold text-white uppercase tracking-wider">
            LAYER 5: DECISION INTELLIGENCE & AEROSPACE MAINTENANCE ADVISOR
          </h2>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          PENDING WORK ORDERS: <strong className="text-slate-200">{maintenance.total_pending_actions}</strong>
        </span>
      </div>

      {/* Urgent Pilot Intervention Banners if any */}
      {urgent_pilot_actions.length > 0 && (
        <div className="mb-4 bg-tactical-red/10 border border-tactical-red/40 rounded-lg p-3 animate-pulse">
          <div className="flex items-center gap-2 text-tactical-red font-mono font-bold text-xs uppercase mb-1">
            <AlertTriangle className="w-4 h-4" />
            IMMEDIATE FLIGHT CREW INTERVENTION MANDATED:
          </div>
          <ul className="list-disc list-inside space-y-1 text-xs font-mono text-slate-200">
            {urgent_pilot_actions.map((act, i) => (
              <li key={i}>{act}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left: Active System Alerts */}
        <div>
          <div className="text-[11px] font-mono font-semibold text-slate-400 uppercase mb-2 flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5 text-tactical-amber" />
            ACTIVE SYSTEM TELEMETRY ALERTS
          </div>
          <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
            {active_alerts.map((alert) => {
              const isCrit = alert.severity === 'CRITICAL';
              const isWarn = alert.severity === 'WARNING';
              return (
                <div
                  key={alert.id}
                  className={`p-2.5 rounded border text-xs font-mono flex items-start gap-2.5 ${
                    isCrit
                      ? 'bg-tactical-red/10 border-tactical-red/40 text-rose-200'
                      : isWarn
                      ? 'bg-tactical-amber/10 border-tactical-amber/40 text-amber-200'
                      : 'bg-space-900 border-space-750 text-slate-300'
                  }`}
                >
                  <span
                    className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase mt-0.5 border ${
                      isCrit
                        ? 'border-tactical-red text-tactical-red'
                        : isWarn
                        ? 'border-tactical-amber text-tactical-amber'
                        : 'border-tactical-emerald text-tactical-emerald'
                    }`}
                  >
                    {alert.severity}
                  </span>
                  <div className="flex-1">
                    <div className="font-semibold text-slate-200 flex justify-between">
                      <span>{alert.system}</span>
                      <span className="text-[10px] text-slate-500">{alert.id}</span>
                    </div>
                    <p className="text-[11px] mt-0.5 text-slate-400">{alert.message}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Work Order Recommendations */}
        <div>
          <div className="text-[11px] font-mono font-semibold text-slate-400 uppercase mb-2 flex items-center gap-1.5">
            <Wrench className="w-3.5 h-3.5 text-tactical-cyan" />
            ACTIONABLE MAINTENANCE WORK ORDERS
          </div>
          <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
            {maintenance_recommendations.map((rec) => (
              <div
                key={rec.code}
                className="bg-space-900/90 p-2.5 rounded border border-space-750 text-xs font-mono hover:border-tactical-cyan/40 transition"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-slate-200 flex items-center gap-1">
                    <span className="text-tactical-cyan">{rec.code}:</span> {rec.title}
                  </span>
                  <span className="text-[10px] bg-space-800 px-1.5 py-0.5 rounded border border-space-700 text-tactical-purple font-semibold">
                    {rec.priority}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed mb-1.5">
                  {rec.procedure}
                </p>
                <div className="flex justify-between text-[10px] text-slate-500 pt-1 border-t border-space-800">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    EST. LABOR: {rec.estimated_hours} HOURS
                  </span>
                  <span className="text-tactical-cyan flex items-center gap-0.5">
                    VIEW CHECKLIST <ChevronRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
