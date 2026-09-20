import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { TopSummary } from './components/TopSummary';
import { GaugesSection } from './components/GaugesSection';
import { DigitalTwinView } from './components/DigitalTwinView';
import { VirtualSensors } from './components/VirtualSensors';
import { AIAnalyticsView } from './components/AIAnalyticsView';
import { TelemetrySimulator } from './components/TelemetrySimulator';
import { MissionSimulator } from './components/MissionSimulator';
import { TrendCharts } from './components/TrendCharts';
import { MaintenancePanel } from './components/MaintenancePanel';
import { OpenAIModal } from './components/OpenAIModal';
import { FlightReportModal } from './components/FlightReportModal';

import { TwinWebSocketClient, WebSocketStatus } from './services/websocket';
import { api } from './services/api';
import { UnifiedTwinState } from './types';

export const App: React.FC = () => {
  const [twinState, setTwinState] = useState<UnifiedTwinState | null>(null);
  const [wsStatus, setWsStatus] = useState<WebSocketStatus>('CONNECTING');
  const [isOpenAIModalOpen, setIsOpenAIModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);

  const wsClientRef = useRef<TwinWebSocketClient | null>(null);

  useEffect(() => {
    // 1. Initial REST fetch for instant display
    api.getTwinState()
      .then((data) => setTwinState(data))
      .catch((err) => console.warn('Initial REST load waiting for backend:', err));

    // 2. Connect live WebSocket (2 Hz streaming)
    const ws = new TwinWebSocketClient();
    wsClientRef.current = ws;

    ws.connect(
      (data: UnifiedTwinState) => {
        setTwinState(data);
      },
      (status: WebSocketStatus) => {
        setWsStatus(status);
      }
    );

    return () => {
      ws.disconnect();
    };
  }, []);

  return (
    <div className="min-h-screen bg-space-950 text-slate-100 flex flex-col p-3 md:p-6 select-none font-sans">
      {/* 1. Command & Control Tactical Header */}
      <Header
        twinState={twinState}
        wsStatus={wsStatus}
        onOpenAIModal={() => setIsOpenAIModalOpen(true)}
        onOpenReportModal={() => setIsReportModalOpen(true)}
      />

      {/* Main Tactical Dashboard Container */}
      <main className="flex-1 flex flex-col gap-1 max-w-[1720px] mx-auto w-full">
        {/* 2. Top Summary KPI Cards (Health, Readiness, Risk, RUL) */}
        <TopSummary twinState={twinState} />

        {/* 3. Core Telemetry Gauges Matrix (With Physics Target Needles) */}
        <GaugesSection twinState={twinState} />

        {/* 4. Digital Twin Engine Schematic & Subsystem States */}
        <DigitalTwinView twinState={twinState} />

        {/* 5. Virtual Sensors */}
        <VirtualSensors virtualSensors={twinState ? twinState.virtual_sensors : null} />

        {/* 6. AI Analytics Layer (Isolation Forest & XGBoost) */}
        <AIAnalyticsView
          anomaly={twinState ? twinState.anomaly : null}
          faults={twinState ? twinState.faults : null}
          rul={twinState ? twinState.rul : null}
          onOpenOpenAI={() => setIsOpenAIModalOpen(true)}
        />

        {/* 7. Real-Time Residual & Actual vs Expected Trend Charts */}
        <TrendCharts twinState={twinState} />

        {/* 8. Mission Profile Simulator Buttons */}
        <MissionSimulator />

        {/* 9. Telemetry Simulation Controls & Fault Injector */}
        <TelemetrySimulator twinState={twinState} />

        {/* 10. Maintenance Advisories & Work Orders */}
        <MaintenancePanel maintenance={twinState ? twinState.maintenance : null} />
      </main>

      {/* Footer System Status */}
      <footer className="mt-6 pt-4 border-t border-space-800 text-center text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-tactical-cyan" />
          <span>AEROTWIN AI DEFENSE-GRADE DIGITAL TWIN ARCHITECTURE</span>
        </div>
        <div>
          <span>UAV POWERTRAIN DIGITAL OBSERVER | ACTIVE STACK: FASTAPI + PYDANTIC + SCIKIT-LEARN + XGBOOST + REACT</span>
        </div>
        <div className="text-slate-400">
          <span>FUTURE ESP8266 MQTT READY</span>
        </div>
      </footer>

      {/* Modals */}
      <OpenAIModal
        isOpen={isOpenAIModalOpen}
        onClose={() => setIsOpenAIModalOpen(false)}
      />

      <FlightReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
      />
    </div>
  );
};

export default App;
