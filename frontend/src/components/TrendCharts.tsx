import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { TrendingUp, RefreshCcw } from 'lucide-react';
import { api } from '../services/api';
import { UnifiedTwinState } from '../types';

interface TrendChartsProps {
  twinState: UnifiedTwinState | null;
}

export const TrendCharts: React.FC<TrendChartsProps> = ({ twinState }) => {
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [viewMode, setViewMode] = useState<'actual_vs_expected' | 'residuals'>('actual_vs_expected');

  // Keep a moving window of recent points for live plotting
  useEffect(() => {
    if (!twinState) return;

    const timeStr = twinState.timestamp ? twinState.timestamp.split('T')[1].slice(0, 8) : '';
    const newPoint = {
      time: timeStr,
      actual_cht: twinState.telemetry.cht,
      expected_cht: twinState.expected_state.expected_cht,
      actual_egt: twinState.telemetry.egt,
      expected_egt: twinState.expected_state.expected_egt,
      cht_residual: twinState.residuals.cht_residual,
      egt_residual: twinState.residuals.egt_residual,
      oil_p_residual: twinState.residuals.oil_p_residual,
      fuel_residual: twinState.residuals.fuel_residual,
    };

    setHistoryData((prev) => {
      const updated = [...prev, newPoint];
      if (updated.length > 30) return updated.slice(updated.length - 30);
      return updated;
    });
  }, [twinState]);

  return (
    <div className="aerospace-panel p-4 mb-4 border-space-700/80">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3 border-b border-space-800 pb-2">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-tactical-cyan" />
          <h2 className="text-xs font-mono font-bold text-white uppercase tracking-wider">
            LAYER 3 & 4: REAL-TIME PHYSICS RESIDUAL & TELEMETRY TRENDS
          </h2>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1 bg-space-900 p-1 rounded-lg border border-space-750 text-xs font-mono">
          <button
            onClick={() => setViewMode('actual_vs_expected')}
            className={`px-3 py-1 rounded transition ${
              viewMode === 'actual_vs_expected'
                ? 'bg-tactical-cyan text-space-950 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            ACTUAL VS EXPECTED OVERLAY
          </button>
          <button
            onClick={() => setViewMode('residuals')}
            className={`px-3 py-1 rounded transition ${
              viewMode === 'residuals'
                ? 'bg-tactical-cyan text-space-950 font-bold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            PHYSICS RESIDUAL DIVERGENCE (Δ)
          </button>
        </div>
      </div>

      <div className="w-full h-64 bg-space-950/60 p-2 rounded-lg border border-space-800">
        <ResponsiveContainer width="100%" height="100%">
          {viewMode === 'actual_vs_expected' ? (
            <LineChart data={historyData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#111E3A" />
              <XAxis dataKey="time" stroke="#64748B" fontSize={10} fontVariant="monospace" />
              <YAxis stroke="#64748B" fontSize={10} fontVariant="monospace" domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#080E1E',
                  borderColor: '#1C315E',
                  borderRadius: '6px',
                  fontFamily: 'monospace',
                  fontSize: '11px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
              {/* Actual CHT */}
              <Line
                type="monotone"
                dataKey="actual_cht"
                name="Actual CHT (°C)"
                stroke="#FF3355"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              {/* Expected CHT */}
              <Line
                type="monotone"
                dataKey="expected_cht"
                name="Physics Expected CHT (°C)"
                stroke="#00E5FF"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                isAnimationActive={false}
              />
              {/* Actual EGT */}
              <Line
                type="monotone"
                dataKey="actual_egt"
                name="Actual EGT (°C)"
                stroke="#FFB300"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              {/* Expected EGT */}
              <Line
                type="monotone"
                dataKey="expected_egt"
                name="Physics Expected EGT (°C)"
                stroke="#A855F7"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          ) : (
            <LineChart data={historyData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#111E3A" />
              <XAxis dataKey="time" stroke="#64748B" fontSize={10} fontVariant="monospace" />
              <YAxis stroke="#64748B" fontSize={10} fontVariant="monospace" domain={['auto', 'auto']} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#080E1E',
                  borderColor: '#1C315E',
                  borderRadius: '6px',
                  fontFamily: 'monospace',
                  fontSize: '11px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
              {/* Residual lines */}
              <Line
                type="monotone"
                dataKey="cht_residual"
                name="CHT Residual (°C)"
                stroke="#FF3355"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="egt_residual"
                name="EGT Residual (°C)"
                stroke="#FFB300"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="oil_p_residual"
                name="Oil Press Residual (PSI)"
                stroke="#00E5FF"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
              <Line
                type="monotone"
                dataKey="fuel_residual"
                name="Fuel Flow Residual (L/h)"
                stroke="#00E676"
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};
