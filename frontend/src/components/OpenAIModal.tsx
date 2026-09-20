import React, { useState } from 'react';
import { X, Sparkles, AlertCircle, CheckCircle2, Copy, Check } from 'lucide-react';
import { api } from '../services/api';
import { AIInsightsData } from '../types';

interface OpenAIModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OpenAIModal: React.FC<OpenAIModalProps> = ({ isOpen, onClose }) => {
  const [apiKey, setApiKey] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState<AIInsightsData | null>(null);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const data = await api.getAIInsights(apiKey);
      setInsights(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!insights) return;
    navigator.clipboard.writeText(JSON.stringify(insights, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="aerospace-panel-glow w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden bg-space-900 border border-purple-500/50 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-space-700 bg-space-850">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400 animate-pulse" />
            <h2 className="text-sm font-bold font-mono text-white tracking-wider uppercase">
              OPENAI PROPULSION INTELLIGENCE & MISSION RISK ADVISOR
            </h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 overflow-y-auto space-y-4 text-xs font-mono">
          {/* API Key Configuration Banner */}
          <div className="bg-space-950 p-3.5 rounded-lg border border-space-750">
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-slate-300 font-semibold uppercase">
                OPENAI API KEY (OPTIONAL OVERRIDE):
              </label>
              <span className="text-[11px] text-slate-400">
                Leave blank to use Server Key / Local Aerospace Expert Engine
              </span>
            </div>
            <div className="flex gap-2">
              <input
                type="password"
                placeholder="sk-... (optional)"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="flex-1 bg-space-900 text-purple-200 px-3 py-1.5 rounded border border-space-700 focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={handleGenerate}
                disabled={loading}
                className="px-4 py-1.5 rounded font-bold bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-md transition disabled:opacity-50 flex items-center gap-1.5"
              >
                {loading ? (
                  <>
                    <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    SYNTHESIZING...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    QUERY AI ADVISOR
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Insights Display */}
          {insights && (
            <div className="space-y-4 animate-fadeIn">
              {/* Source Pill & Copy */}
              <div className="flex items-center justify-between bg-space-950 px-3 py-2 rounded border border-space-800">
                <span className="text-[11px] text-slate-400">
                  DIAGNOSTIC ENGINE:{' '}
                  <strong className="text-purple-400">{insights.llm_source}</strong>
                </span>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-[11px] text-slate-300 hover:text-white bg-space-800 px-2 py-0.5 rounded border border-space-700 transition"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  {copied ? 'COPIED JSON' : 'COPY JSON'}
                </button>
              </div>

              {/* 1. Maintenance Report */}
              <div className="bg-space-950 p-3.5 rounded-lg border border-space-750">
                <div className="text-purple-400 font-bold uppercase mb-1">
                  1. PROPULSION MAINTENANCE REPORT
                </div>
                <p className="text-slate-300 leading-relaxed">
                  {insights.ai_maintenance_report}
                </p>
              </div>

              {/* 2. Mission Risk Assessment */}
              <div className="bg-space-950 p-3.5 rounded-lg border border-space-750">
                <div className="text-amber-400 font-bold uppercase mb-1">
                  2. TACTICAL MISSION RISK ASSESSMENT
                </div>
                <p className="text-slate-300 leading-relaxed">
                  {insights.ai_mission_risk_assessment}
                </p>
              </div>

              {/* 3. Physics Root Cause Analysis */}
              <div className="bg-space-950 p-3.5 rounded-lg border border-space-750">
                <div className="text-tactical-cyan font-bold uppercase mb-1">
                  3. PHYSICS RESIDUAL ROOT CAUSE ANALYSIS
                </div>
                <p className="text-slate-300 leading-relaxed">
                  {insights.ai_root_cause_analysis}
                </p>
              </div>

              {/* 4. Recommended Actions */}
              <div className="bg-space-950 p-3.5 rounded-lg border border-space-750">
                <div className="text-tactical-emerald font-bold uppercase mb-2">
                  4. RECOMMENDED MULTI-TIER ACTION PROTOCOLS
                </div>
                <ul className="space-y-1.5 list-disc list-inside text-slate-300">
                  {insights.ai_recommended_actions.map((act, i) => (
                    <li key={i} className="leading-relaxed">
                      {act}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-space-800 bg-space-850 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-space-800 hover:bg-space-750 text-slate-300 border border-space-700 text-xs font-mono font-bold transition"
          >
            DISMISS
          </button>
        </div>
      </div>
    </div>
  );
};
