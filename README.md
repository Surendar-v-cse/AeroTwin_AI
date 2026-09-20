# AeroTwin AI — MALE UAV Aero-Piston Engine Digital Twin Platform

AeroTwin AI is a defense-grade Digital Twin platform for Medium-Altitude Long-Endurance (MALE) Unmanned Aerial Vehicle (UAV) aero-piston engines (e.g., Rotax 914/915 turbocharged series, powering aircraft such as Predator MQ-1, Bayraktar TB2, and Hermes 450).

Rather than a simple dashboard, AeroTwin AI operates as a true **Digital Twin System**: a virtual engine that continuously receives telemetry, maintains internal multi-subsystem states, computes first-principles physics baselines and residuals, performs multi-model AI analytics, assesses structural health, estimates Remaining Useful Life (RUL), and delivers tactical maintenance advisories.

---

## System Architecture (6-Layer Design)

```
┌─────────────────────────────────────────────────────────────┐
│               LAYER 6: VISUALIZATION DASHBOARD              │
│  Tactical C2 UI · SVG Arc Dials · Expected Target Notches   │
│  Engine Schematic · AI Anomaly Radar · Trend Timeline       │
└──────────────────────────────┬──────────────────────────────┘
                               │ WebSocket (2 Hz) / REST
┌──────────────────────────────▼──────────────────────────────┐
│             LAYER 5: DECISION INTELLIGENCE                  │
│  Composite Health Scorer (0-100) · Mission Readiness Engine │
│  Tactical Risk Assessor · Work Order Maintenance Advisor    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  LAYER 4: AI ANALYTICS                      │
│  1. Isolation Forest Anomaly Detection (Normal/Warn/Crit)   │
│  2. XGBoost Multi-Class Fault Classifier (7 Failure Modes)  │
│  3. Real-Time Moving Derivative Trend Analyzer              │
│  4. Physics-Informed RUL Engine (Arrhenius + Miner's Rule)  │
│  5. Digital Twin Virtual Sensor Engine (Efficiency, Stress) │
│  6. OpenAI Autonomous Propulsion Advisor (LLM + Local Expert)│
└──────────────────────────────┬──────────────────────────────┘
                               │ Physics Residuals (Actual - Expected)
┌──────────────────────────────▼──────────────────────────────┐
│                 LAYER 3: PHYSICS ENGINE                     │
│  ISA Atmosphere Model (0-25k ft) · Turbocharger Boost Model │
│  Expected EGT/CHT Formulas · BSFC Specific Fuel Flow Model  │
│  Residual Calculator: R = Actual - Expected                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│               LAYER 2: DIGITAL TWIN CORE                    │
│  Virtual Engine Representation · Subsystem State Observers  │
│  Thermal · Mechanical · Combustion · Lubrication · Fuel     │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│             LAYER 1: TELEMETRY SIMULATION                   │
│  Mode A: Manual Sliders · Mode B: Auto-Physics Couplings    │
│  Fault Injector Harness (Injector, Oil, Cooling, Drift)     │
│  [Future Hardware: ESP8266 MQTT Client Plug-and-Play]       │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. Telemetry Simulation Layer (Mode A & Mode B)
- **Manual Mode (Mode A)**: Direct slider control over RPM (1000-7000), EGT (300-900°C), CHT (50-300°C), Oil Temp (20-150°C), Oil Pressure (10-120 PSI), Fuel Flow (0-100 L/h), Altitude (0-25,000 ft), Ambient Temp (-20 to 60°C), Humidity (0-100%), and Throttle (0-100%).
- **Auto Mode (Mode B)**: Realistic physical couplings with first-order thermal/mechanical inertia filters:
  - Throttle $\uparrow \implies$ RPM $\uparrow$, Fuel Flow $\uparrow$, EGT curve.
  - Altitude $\uparrow \implies$ ISA Air Density $\sigma \downarrow$, turbo wastegate boost limits.
  - High Ambient Temp $\implies$ CHT cooling margin degradation.
- **Physical Fault Injectors**: One-click simulation of Injector Clog, Oil System Leak, Radiator Duct Blockage, and Sensor Drift.

### 2. Digital Twin Core & Subsystems
Maintains a virtual state representation across five key subsystems:
- **Thermal State**: Heat flux (kW), CHT/EGT redline margins, cooling reserve %, thermal stress index.
- **Mechanical State**: Brake horsepower (HP), torque (Nm), vibration risk index, overspeed margin.
- **Combustion State**: Air-fuel stoichiometry ($\lambda$), AFR, combustion stability score, detonation risk.
- **Lubrication State**: Kinematic viscosity (cSt), hydrodynamic oil film integrity, scavenge margin.
- **Fuel System State**: Injector duty cycle %, delivery compliance %, vapor lock risk index.

### 3. Physics Engine & Residuals
Calculates theoretical equilibrium values based on thermodynamics and aerodynamics:
- $R_{\text{EGT}} = \text{Actual EGT} - \text{Expected EGT}$
- $R_{\text{CHT}} = \text{Actual CHT} - \text{Expected CHT}$
- $R_{\text{OilP}} = \text{Actual OilP} - \text{Expected OilP}$
- $R_{\text{Fuel}} = \text{Actual Fuel} - \text{Expected Fuel}$
These residuals are visualized on gauges and charts, and fed into AI models for high-signal fault isolation.

### 4. AI Analytics Layer
- **Anomaly Detection (Isolation Forest)**: Multi-variate outlier detection outputting Anomaly Score (0.0 to 1.0), Status (`Normal`, `Warning`, `Critical`), and top outlier feature.
- **Fault Classifier (XGBoost / Random Forest)**: Classifies among 8 operational signatures: Nominal Operation, Injector Fault, Lubrication Issue, Cooling Failure, Combustion Instability, Sensor Failure, Overheating, and Fuel System Degradation.
- **RUL Engine (Remaining Useful Life)**: Arrhenius thermal fatigue and cumulative Miner's rule damage accumulation estimating Remaining Flight Hours, Engine Health %, and 50-hour In-Flight Shutdown (IFSD) risk.
- **Virtual Sensors**: Real-time synthesized parameters: Engine Efficiency (%), Cylinder Thermal Stress, Wear Index, Combustion Quality, and Overall Health Index.
- **OpenAI Propulsion Advisor**: Structured generative AI flight engineer reports (`ai_maintenance_report`, `ai_mission_risk_assessment`, `ai_root_cause_analysis`, `ai_recommended_actions`) with automated local heuristic fallback when offline.

### 5. Future-Ready ESP8266 MQTT Telemetry Integration
The `backend/telemetry/` directory implements an abstract `TelemetryProvider` interface. The software simulator can be substituted with `MqttTelemetryProvider` (which connects to MQTT broker topic `aerotwin/uav/telemetry` for ESP8266 Wi-Fi microcontroller telemetry) with **zero changes** to the Digital Twin, Physics Engine, AI Analytics, or UI.

---

## Running the Platform

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Service
```bash
# From repository root:
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
- API Swagger Documentation: `http://localhost:8000/docs`
- Live WebSocket Stream: `ws://localhost:8000/ws/telemetry`

### 2. Frontend C2 Dashboard
```bash
cd frontend
npm install
npm run dev
```
- Dashboard URL: `http://localhost:5173`

---

## REST Endpoints Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/telemetry` | `GET` | Retrieve latest telemetry snapshot |
| `/api/telemetry` | `POST` | Update manual telemetry parameters |
| `/api/telemetry/mode` | `POST` | Switch between `manual` and `auto` mode |
| `/api/telemetry/inject-fault` | `POST` | Inject or clear physical engine fault |
| `/api/twin` | `GET` | Retrieve full synchronized Digital Twin state |
| `/api/twin/residuals` | `GET` | Retrieve physics residuals (Actual - Expected) |
| `/api/anomaly` | `GET` | Isolation Forest anomaly score and status |
| `/api/faults` | `GET` | XGBoost multi-class fault classification & confidence |
| `/api/rul` | `GET` | Remaining Useful Life hours and explainable breakdown |
| `/api/health` | `GET` | Composite Health Score and Mission Readiness |
| `/api/simulation` | `POST` | Trigger mission profiles (High Altitude, Hot Weather, Endurance, Emergency, Nominal) |
| `/api/maintenance` | `GET` | Active maintenance alerts and actionable work orders |
| `/api/mission-report` | `GET` | Comprehensive airworthiness telemetry certification log |
| `/api/ai-insights` | `POST` | OpenAI or Local Aerospace Expert propulsion report |
| `/ws/telemetry` | `WS` | 2 Hz high-frequency live unified state broadcast |
