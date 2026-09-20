import React, { useState, useEffect } from 'react';
import { Shield, Radio, Activity, Cpu, Sparkles, Terminal } from 'lucide-react';
import { UnifiedTwinState } from '../types';

interface HeaderProps {
  twinState: UnifiedTwinState | null;
  wsStatus: string;
  onOpenAIModal: () => void;
  onOpenReportModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  twinState,
  wsStatus,
  onOpenAIModal,
  onOpenReportModal
}) => {
  const [currentTime, setCurrentTime] = useState(new Date().toUTCString());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date().toUTCString()), 1000);
    return () => clearInterval(timer);
  }, []);

  const readiness = twinState?.readiness.mission_readiness || 'INITIALIZING';
  const readinessColor =
    readiness === 'Ready'
      ? 'text-tactical-emerald border-tactical-emerald/40 bg-tactical-emerald/10'
      : readiness === 'Ready with Monitoring'
      ? 'text-tactical-cyan border-tactical-cyan/40 bg-tactical-cyan/10'
      : readiness === 'Maintenance Recommended'
      ? 'text-tactical-amber border-tactical-amber/40 bg-tactical-amber/10'
      : 'text-tactical-red border-tactical-red/40 bg-tactical-red/10 animate-pulse';

  return (
    <header className="aerospace-panel px-4 py-3 border-b border-space-700/80 mb-4 sticky top-0 z-40">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left: Platform Branding */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-tactical-cyan/20 to-blue-600/30 border border-tactical-cyan/50 flex items-center justify-center shadow-hud-cyan">
            <Cpu className="w-5 h-5 text-tactical-cyan animate-pulse-slow" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-wider text-white font-mono flex items-center gap-1.5">
                AERO<span className="text-tactical-cyan">TWIN</span>
                <span className="text-xs bg-space-800 text-tactical-cyan px-1.5 py-0.5 rounded border border-tactical-cyan/30">
                  AI DIGITAL TWIN
                </span>
              </h1>
            </div>
            <div className="text-xs text-slate-400 font-mono flex items-center gap-2">
              <span>UAV-C2: <strong className="text-slate-200">AEROTWIN-01</strong></span>
              <span className="text-slate-600">|</span>
              <span>POWERTRAIN: <strong className="text-slate-300">ROTAX 914-TURBO</strong></span>
            </div>
          </div>
        </div>

        {/* Center: Mission Status & Phase */}
        <div className="hidden lg:flex items-center gap-4 bg-space-900/90 px-4 py-1.5 rounded-md border border-space-750">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-tactical-cyan animate-pulse" />
            <span className="text-xs text-slate-400 uppercase font-mono">PHASE:</span>
            <span className="text-sm font-semibold text-tactical-cyan font-mono">
              {twinState?.telemetry.mission_phase || 'CRUISE'}
            </span>
          </div>
          <div className="h-4 w-px bg-space-700" />
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 uppercase font-mono">STATUS:</span>
            <span className={`text-xs px-2 py-0.5 rounded font-mono font-medium border ${readinessColor}`}>
              {readiness}
            </span>
          </div>
          <div className="h-4 w-px bg-space-700" />
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-slate-400 font-mono">ALT:</span>
            <span className="text-xs font-mono text-slate-200 font-bold">
              {twinState ? Math.round(twinState.telemetry.altitude).toLocaleString() : '12,000'} FT
            </span>
          </div>
        </div>

        {/* Right: Actions, Live Ping & UTC Clock */}
        <div className="flex items-center gap-3">
          {/* Mission Report Button */}
          <button
            onClick={onOpenReportModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono font-semibold bg-space-800 hover:bg-space-750 text-slate-200 border border-space-700 transition"
          >
            <Terminal className="w-3.5 h-3.5 text-tactical-cyan" />
            <span>FLIGHT LOG</span>
          </button>

          {/* OpenAI Insights Button */}
          <button
            onClick={onOpenAIModal}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono font-semibold bg-gradient-to-r from-purple-900/60 to-space-800 hover:from-purple-800/80 hover:to-space-750 text-purple-200 border border-purple-500/40 shadow-sm transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400 animate-pulse" />
            <span>AI PROPULSION ADVISOR</span>
          </button>

          {/* WS Connection Pill */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-space-900 border border-space-750 text-xs font-mono">
            <span
              className={`w-2 h-2 rounded-full ${
                wsStatus === 'CONNECTED'
                  ? 'bg-tactical-emerald shadow-[0_0_8px_#00E676]'
                  : wsStatus === 'CONNECTING'
                  ? 'bg-tactical-amber animate-ping'
                  : 'bg-tactical-red'
              }`}
            />
            <span className="text-slate-400 text-[11px] uppercase">
              {wsStatus === 'CONNECTED' ? 'LIVE TWIN (2 HZ)' : wsStatus}
            </span>
          </div>

          {/* Clock */}
          <div className="hidden xl:block text-right font-mono text-[11px] text-slate-400 pl-2 border-l border-space-750">
            <div className="text-slate-200 font-semibold">{currentTime.split(' ')[4]} UTC</div>
            <div className="text-[10px] text-slate-500">DEFENSE PROTOCOL V1.0</div>
          </div>
        </div>
      </div>
    </header>
  );
};
