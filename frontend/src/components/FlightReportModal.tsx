import React, { useState, useEffect } from 'react';
import { X, FileText, Download, CheckCircle } from 'lucide-react';
import { api } from '../services/api';

interface FlightReportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const FlightReportModal: React.FC<FlightReportModalProps> = ({ isOpen, onClose }) => {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      api.getMissionReport()
        .then((data) => setReport(data))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleDownload = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AEROTWIN_MISSION_REPORT_${new Date().toISOString().slice(0, 19)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="aerospace-panel-glow w-full max-w-2xl max-h-[85vh] flex flex-col overflow-hidden bg-space-900 border border-tactical-cyan/40 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-space-700 bg-space-850">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-tactical-cyan" />
            <h2 className="text-sm font-bold font-mono text-white tracking-wider uppercase">
              UAV PROPULSION HEALTH & AIRWORTHINESS CERTIFICATION LOG
            </h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto space-y-4 text-xs font-mono">
          {loading ? (
            <div className="text-center py-8 text-slate-400">Loading flight telemetry report...</div>
          ) : report ? (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3 bg-space-950 p-3 rounded border border-space-800">
                <div>AIRCRAFT: <strong className="text-slate-200">{report.aircraft_callsign}</strong></div>
                <div>ENGINE: <strong className="text-slate-200">{report.engine_type}</strong></div>
                <div>TIMESTAMP: <strong className="text-slate-400">{report.timestamp}</strong></div>
                <div>MISSION PHASE: <strong className="text-tactical-cyan">{report.mission_phase}</strong></div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-space-950 p-3 rounded border border-space-800">
                <div>HEALTH SCORE: <strong className="text-tactical-emerald">{report.health_score}/100</strong></div>
                <div>READINESS: <strong className="text-slate-200">{report.mission_readiness}</strong></div>
                <div>RUL REMAINING: <strong className="text-tactical-purple">{report.rul_hours_remaining} hrs</strong></div>
                <div>50H IFSD RISK: <strong className="text-slate-200">{report['50h_failure_probability_pct']}%</strong></div>
                <div>DETECTED FAULT: <strong className="text-tactical-amber">{report.predicted_fault}</strong></div>
                <div>CONFIDENCE: <strong className="text-slate-200">{report.fault_confidence_pct}%</strong></div>
              </div>

              <div className="bg-space-950 p-3 rounded border border-space-800 space-y-1 text-slate-300">
                <div>THERMAL STRESS INDEX: {report.cylinder_thermal_stress_index} / 100</div>
                <div>ENGINE EFFICIENCY: {report.engine_efficiency_pct}%</div>
                <div>ACTIVE TELEMETRY ALERTS: {report.active_maintenance_alerts}</div>
                <div>PENDING RECOMMENDATIONS: {report.recommendations_count}</div>
              </div>

              <div className="text-emerald-400 flex items-center gap-1.5 pt-2">
                <CheckCircle className="w-4 h-4" />
                <span>Verified by AeroTwin AI First-Principles Physics & AI Residual Stack</span>
              </div>
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-space-800 bg-space-850 flex justify-between">
          <button
            onClick={handleDownload}
            disabled={!report}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-tactical-cyan text-space-950 font-mono font-bold text-xs hover:bg-tactical-cyan/80 transition"
          >
            <Download className="w-3.5 h-3.5" />
            EXPORT MISSION LOG
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-space-800 hover:bg-space-750 text-slate-300 border border-space-700 text-xs font-mono font-bold transition"
          >
            CLOSE
          </button>
        </div>
      </div>
    </div>
  );
};
