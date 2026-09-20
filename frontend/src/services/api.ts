import { UnifiedTwinState, AIInsightsData } from '../types';

const API_BASE = 'http://localhost:8000';

export const api = {
  async getTwinState(): Promise<UnifiedTwinState> {
    const res = await fetch(`${API_BASE}/api/twin`);
    if (!res.ok) throw new Error('Failed to fetch twin state');
    return res.json();
  },

  async updateTelemetry(updateData: Record<string, any>): Promise<any> {
    const res = await fetch(`${API_BASE}/api/telemetry`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData),
    });
    if (!res.ok) throw new Error('Failed to update telemetry');
    return res.json();
  },

  async setSimulatorMode(mode: 'manual' | 'auto'): Promise<any> {
    const res = await fetch(`${API_BASE}/api/telemetry/mode?mode=${mode}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to set mode');
    return res.json();
  },

  async injectFault(faultType: string, severity: number = 1.0): Promise<any> {
    const res = await fetch(`${API_BASE}/api/telemetry/inject-fault`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fault_type: faultType, severity }),
    });
    if (!res.ok) throw new Error('Failed to inject fault');
    return res.json();
  },

  async triggerScenario(scenario: string): Promise<any> {
    const res = await fetch(`${API_BASE}/api/simulation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario }),
    });
    if (!res.ok) throw new Error('Failed to trigger simulation scenario');
    return res.json();
  },

  async getAIInsights(apiKey?: string): Promise<AIInsightsData> {
    const res = await fetch(`${API_BASE}/api/ai-insights`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey || '' }),
    });
    if (!res.ok) throw new Error('Failed to generate AI insights');
    return res.json();
  },

  async getTelemetryHistory(limit: number = 60): Promise<any[]> {
    const res = await fetch(`${API_BASE}/api/telemetry/history?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch telemetry history');
    return res.json();
  },

  async getResidualsHistory(limit: number = 60): Promise<any[]> {
    const res = await fetch(`${API_BASE}/api/twin/residuals/history?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch residuals history');
    return res.json();
  },

  async getMissionReport(): Promise<any> {
    const res = await fetch(`${API_BASE}/api/mission-report`);
    if (!res.ok) throw new Error('Failed to fetch mission report');
    return res.json();
  }
};
