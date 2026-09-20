import React from 'react';
import { ShieldCheck, AlertTriangle, Crosshair, BarChart3, HelpCircle, Activity } from 'lucide-react';
import { AnomalyData, FaultsData, RULData } from '../types';

interface AIAnalyticsViewProps {
  anomaly: AnomalyData | null;
  faults: FaultsData | null;
  rul: RULData | null;
  onOpenOpenAI: () => void;
}

export const AIAnalyticsView: React.FC<AIAnalyticsViewProps> = ({
  anomaly,
  faults,
  rul,
  onOpenOpenAI
}) => {
  if (!anomaly || !faults || !rul) return null;

  // Anomaly status color
  const anomalyColor =
    anomaly.anomaly_status === 'Normal'
      ? 'text-tactical-emerald border-tactical-emerald/30 bg-tactical-emerald/10'
      : anomaly.anomaly_status === 'Warning'
      ? 'text-tactical-amber border-tactical-amber/30 bg-tactical-amber/10'
      : 'text-tactical-red border-tactical-red/30 bg-tactical-red/10 animate-pulse';

  const faultSorted = Object.entries(faults.probability_distribution).sort((a, b) => b[1] - a[1]);

  return (
    <div className="aerospace-panel p-4 mb-4 border-space-700/80">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-4 border-b border-space-800 pb-2">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-tactical-purple" />
          <h2 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wider">
            AI PROPULSION ANALYTICS (ISOLATION FOREST & XGBOOST CLASSIFIER)
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-slate-400">
            ENGINE ALGORITHM: <strong className="text-tactical-purple">{faults.model_type}</strong>
          </span>
          <button
            onClick={onOpenOpenAI}
            className="text-xs font-mono font-bold text-tactical-cyan bg-tactical-cyan/10 hover:bg-tactical-cyan/20 px-2 py-0.5 rounded border border-tactical-cyan/30 transition"
          >
            GENERATE AI DIAGNOSTIC REPORT
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* 1. Isolation Forest Anomaly Radar Card */}
        <div className="bg-space-900/90 p-3.5 rounded-lg border border-space-750 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span className="font-semibold uppercase flex items-center gap-1.5">
                <Crosshair className="w-3.5 h-3.5 text-tactical-cyan" />
                ISOLATION FOREST ANOMALY
              </span>
              <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border uppercase ${anomalyColor}`}>
                {anomaly.anomaly_status}
              </span>
            </div>

            <div className="flex items-baseline justify-between mt-3">
              <div>
                <div className="text-[11px] font-mono text-slate-400">ANOMALY SCORE</div>
                <div className={`text-3xl font-black font-mono ${
                  anomaly.anomaly_status === 'Normal' ? 'text-tactical-emerald' : anomaly.anomaly_status === 'Warning' ? 'text-tactical-amber' : 'text-tactical-red'
                }`}>
                  {anomaly.anomaly_score.toFixed(3)}
                </div>
              </div>
              <div className="text-right text-[11px] font-mono text-slate-400">
                <div>Confidence: <span className="text-slate-200">{anomaly.confidence_pct}%</span></div>
                <div>Decision: <span className="text-slate-400">{anomaly.raw_decision_score}</span></div>
              </div>
            </div>

            {/* Score Bar */}
            <div className="w-full bg-space-800 h-2 rounded-full mt-3 overflow-hidden relative">
              <div
                className={`h-full transition-all duration-500 rounded-full ${
                  anomaly.anomaly_score > 0.65 ? 'bg-tactical-red' : anomaly.anomaly_score > 0.35 ? 'bg-tactical-amber' : 'bg-tactical-emerald'
                }`}
                style={{ width: `${Math.min(100, Math.max(5, anomaly.anomaly_score * 100))}%` }}
              />
              {/* Threshold indicator marks */}
              <div className="absolute top-0 bottom-0 left-[35%] w-0.5 bg-yellow-500/50" title="Warning threshold" />
              <div className="absolute top-0 bottom-0 left-[65%] w-0.5 bg-red-500/50" title="Critical threshold" />
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-space-800 text-xs font-mono flex items-center justify-between text-slate-400">
            <span>Primary Outlier Driver:</span>
            <span className="text-slate-200 font-bold bg-space-800 px-2 py-0.5 rounded border border-space-700 truncate max-w-[170px]">
              {anomaly.top_contributor}
            </span>
          </div>
        </div>

        {/* 2. XGBoost Multi-Class Fault Classification */}
        <div className="bg-space-900/90 p-3.5 rounded-lg border border-space-750 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span className="font-semibold uppercase flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-tactical-purple" />
                FAULT CLASSIFICATION
              </span>
              <span className="text-[10px] font-mono text-tactical-purple font-semibold">
                CONF: {faults.confidence_pct}%
              </span>
            </div>

            <div className="mt-2">
              <div className="text-[11px] font-mono text-slate-400">DETECTED SIGNATURE:</div>
              <div className="text-lg font-bold font-mono text-white flex items-center gap-2">
                <span className={faults.is_critical ? 'text-tactical-red' : faults.predicted_fault === 'Nominal Operation' ? 'text-tactical-emerald' : 'text-tactical-amber'}>
                  {faults.predicted_fault}
                </span>
              </div>
            </div>

            {/* Probability Bars (Top 4) */}
            <div className="mt-3 flex flex-col gap-1.5">
              {faultSorted.slice(0, 4).map(([fName, prob]) => (
                <div key={fName} className="text-[11px] font-mono">
                  <div className="flex justify-between text-slate-400 mb-0.5">
                    <span className="truncate max-w-[180px]">{fName}</span>
                    <span className="text-slate-200">{prob.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-space-800 h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        fName === 'Nominal Operation'
                          ? 'bg-tactical-emerald'
                          : prob > 40
                          ? 'bg-tactical-red'
                          : 'bg-tactical-purple'
                      }`}
                      style={{ width: `${Math.max(1, prob)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-space-800 text-[10px] font-mono text-slate-500 text-right">
            Synthetic Physics-Trained Signature Bank
          </div>
        </div>

        {/* 3. Explainable Cumulative RUL & Degradation Attribution */}
        <div className="bg-space-900/90 p-3.5 rounded-lg border border-space-750 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-xs font-mono text-slate-400 mb-2">
              <span className="font-semibold uppercase flex items-center gap-1.5">
                <HelpCircle className="w-3.5 h-3.5 text-tactical-cyan" />
                EXPLAINABLE DEGRADATION
              </span>
              <span className="text-[10px] font-mono text-tactical-cyan font-semibold">
                ARRHENIUS & MINER
              </span>
            </div>

            <div className="text-[11px] font-mono text-slate-400 mt-2">
              DEGRADATION CONTRIBUTION FACTORS:
            </div>

            <div className="mt-3 space-y-2 text-xs font-mono">
              <div>
                <div className="flex justify-between text-slate-300 text-[11px] mb-0.5">
                  <span>Thermal Aging (Arrhenius CHT):</span>
                  <strong className="text-tactical-red">{rul.explainability.thermal_fatigue_contribution_pct}%</strong>
                </div>
                <div className="w-full bg-space-800 h-1.5 rounded-full overflow-hidden">
                  <div className="h-full bg-tactical-red rounded-full" style={{ width: `${rul.explainability.thermal_fatigue_contribution_pct}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 text-[11px] mb-0.5">
                  <span>Mechanical Stress (RPM / Load):</span>
                  <strong className="text-tactical-cyan">{rul.explainability.mechanical_stress_contribution_pct}%</strong>
                </div>
                <div className="w-full bg-space-800 h-1.5 rounded-full overflow-hidden">
                  <div className="h-full bg-tactical-cyan rounded-full" style={{ width: `${rul.explainability.mechanical_stress_contribution_pct}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 text-[11px] mb-0.5">
                  <span>Oil Film Degradation:</span>
                  <strong className="text-tactical-amber">{rul.explainability.oil_degradation_contribution_pct}%</strong>
                </div>
                <div className="w-full bg-space-800 h-1.5 rounded-full overflow-hidden">
                  <div className="h-full bg-tactical-amber rounded-full" style={{ width: `${rul.explainability.oil_degradation_contribution_pct}%` }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 text-[11px] mb-0.5">
                  <span>Residual Deviation Penalty:</span>
                  <strong className="text-tactical-purple">{rul.explainability.residual_anomaly_contribution_pct}%</strong>
                </div>
                <div className="w-full bg-space-800 h-1.5 rounded-full overflow-hidden">
                  <div className="h-full bg-tactical-purple rounded-full" style={{ width: `${rul.explainability.residual_anomaly_contribution_pct}%` }} />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-3 pt-2 border-t border-space-800 text-[10px] font-mono text-slate-400 flex justify-between">
            <span>Fleet Accumulated Hours:</span>
            <strong className="text-slate-200">{rul.accumulated_hours} hrs</strong>
          </div>
        </div>
      </div>
    </div>
  );
};
