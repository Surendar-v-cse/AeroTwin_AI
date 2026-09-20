export interface TelemetryData {
  timestamp: string;
  rpm: number;
  egt: number;
  cht: number;
  oil_temp: number;
  oil_press: number;
  fuel_flow: number;
  altitude: number;
  ambient_temp: number;
  humidity: number;
  throttle: number;
  mission_phase: string;
  source: string;
}

export interface ExpectedState {
  expected_egt: number;
  expected_cht: number;
  expected_fuel_flow: number;
  expected_oil_temp: number;
  expected_oil_press: number;
  expected_thermal_stress: number;
  expected_efficiency: number;
  expected_power_hp: number;
  air_density_sigma: number;
}

export interface Residuals {
  egt_residual: number;
  cht_residual: number;
  fuel_residual: number;
  oil_p_residual: number;
  oil_t_residual: number;
  thermal_stress_residual: number;
  efficiency_residual: number;
}

export interface ThermalState {
  status: string;
  cht_margin_c: number;
  egt_margin_c: number;
  thermal_gradient_c: number;
  heat_flux_kw: number;
  thermal_stress_index: number;
  cooling_reserve_pct: number;
}

export interface MechanicalState {
  status: string;
  power_output_hp: number;
  torque_nm: number;
  mechanical_stress_index: number;
  vibration_risk_index: number;
  overspeed_margin_rpm: number;
}

export interface CombustionState {
  status: string;
  lambda_ratio: number;
  estimated_afr: number;
  combustion_quality_score: number;
  detonation_risk_index: number;
  misfire_risk_pct: number;
}

export interface LubricationState {
  status: string;
  viscosity_cst: number;
  oil_film_integrity: number;
  lubrication_degradation_index: number;
  scavenge_pressure_margin_psi: number;
}

export interface FuelState {
  status: string;
  injector_duty_cycle_pct: number;
  delivery_compliance_pct: number;
  vapor_lock_risk_index: number;
  fuel_rail_pressure_margin: string;
}

export interface Subsystems {
  thermal_state: ThermalState;
  mechanical_state: MechanicalState;
  combustion_state: CombustionState;
  lubrication_state: LubricationState;
  fuel_state: FuelState;
}

export interface PredictedState {
  horizon_sec: number;
  projected_cht: number;
  projected_egt: number;
  projected_oil_temp: number;
  projected_oil_press: number;
  cht_rate_c_per_sec?: number;
  thermal_trajectory: string;
}

export interface AnomalyData {
  anomaly_score: number;
  anomaly_status: 'Normal' | 'Warning' | 'Critical';
  raw_decision_score: number;
  top_contributor: string;
  confidence_pct: number;
}

export interface FaultsData {
  predicted_fault: string;
  confidence_pct: number;
  is_critical: boolean;
  probability_distribution: Record<string, number>;
  model_type: string;
}

export interface TrendsData {
  temperature_trend: string;
  oil_trend: string;
  fuel_trend: string;
  health_trend: string;
  d_cht_dt: number;
  d_oil_t_dt: number;
  d_health_dt: number;
  recent_history: Array<{
    timestamp: string;
    cht: number;
    egt: number;
    oil_temp: number;
    oil_press: number;
    fuel_flow: number;
    health_score: number;
  }>;
}

export interface RULData {
  hours_remaining: number;
  nominal_tbo_hours: number;
  accumulated_hours: number;
  engine_health_pct: number;
  failure_probability_50h_pct: number;
  composite_wear_rate: number;
  explainability: {
    thermal_fatigue_contribution_pct: number;
    mechanical_stress_contribution_pct: number;
    oil_degradation_contribution_pct: number;
    residual_anomaly_contribution_pct: number;
  };
}

export interface VirtualSensorsData {
  engine_efficiency_pct: number;
  cylinder_thermal_stress_index: number;
  wear_index: number;
  combustion_quality_score: number;
  overall_health_index: number;
  virtual_sensor_status: string;
}

export interface HealthData {
  health_score: number;
  health_category: 'Excellent' | 'Good' | 'Warning' | 'Critical';
  status_color: string;
  deductions: {
    anomaly_deduction: number;
    physics_residual_deduction: number;
    operational_limit_deduction: number;
  };
}

export interface ReadinessData {
  mission_readiness: 'Ready' | 'Ready with Monitoring' | 'Maintenance Recommended' | 'Not Mission Ready';
  badge_color: string;
  description: string;
  flight_authorized: boolean;
}

export interface MaintenanceAlert {
  id: string;
  severity: string;
  system: string;
  message: string;
  timestamp: string;
}

export interface MaintenanceRecommendation {
  code: string;
  title: string;
  priority: string;
  estimated_hours: number;
  procedure: string;
}

export interface MaintenanceData {
  active_alerts: MaintenanceAlert[];
  maintenance_recommendations: MaintenanceRecommendation[];
  urgent_pilot_actions: string[];
  total_pending_actions: number;
}

export interface UnifiedTwinState {
  timestamp: string;
  telemetry: TelemetryData;
  simulation_mode: 'manual' | 'auto';
  active_fault: string;
  expected_state: ExpectedState;
  residuals: Residuals;
  residual_magnitude: number;
  subsystems: Subsystems;
  predicted_state: PredictedState;
  anomaly: AnomalyData;
  faults: FaultsData;
  trends: TrendsData;
  rul: RULData;
  virtual_sensors: VirtualSensorsData;
  health: HealthData;
  readiness: ReadinessData;
  maintenance: MaintenanceData;
}

export interface AIInsightsData {
  ai_maintenance_report: string;
  ai_mission_risk_assessment: string;
  ai_root_cause_analysis: string;
  ai_recommended_actions: string[];
  llm_source?: string;
  error_detail?: string;
}
