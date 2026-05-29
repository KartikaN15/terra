export interface Production {
  production_id: string;
  title: string;
  type: string;
  genre: string | null;
  budget_band: string | null;
  runtime_min: number | null;
  episodes: number;
  shoot_days: number | null;
  locations: string[];
  cast_count: number | null;
  crew_count: number | null;
  vfx_intensity: string | null;
  status: string;
  carbon_budget_tco2e: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProductionSummary {
  production_id: string;
  total_tco2e: number;
  scope_breakdown: Record<string, number>;
  category_breakdown: Record<string, number>;
  phase_breakdown: Record<string, number>;
  overall_confidence: number;
  budget_variance_percent: number | null;
  event_count: number;
  tier_1_percent: number;
  tier_2_percent: number;
  tier_3_percent: number;
  intensity_tco2e_per_hour: number | null;
  intensity_tco2e_per_episode: number | null;
}

export interface GreenlightForecast {
  project_id: string;
  predicted_total_tco2e: number;
  interval_lower_tco2e: number;
  interval_upper_tco2e: number;
  confidence: number;
  top_driver: string;
  model_version: string;
}

export interface ActivityEvent {
  event_id: string;
  production_id: string;
  phase: string;
  scope: string;
  category: string;
  subcategory: string;
  value: string;
  unit: string;
  kgco2e: string;
  kgco2e_wtt: string | null;
  confidence_tier: string;
  confidence_score: string;
  source_type: string;
  source_reference: string | null;
  grid_region: string | null;
  recorded_at: string;
  recorded_by: string;
  calculated_at: string;
  gwp_version: string | null;
  region_match: string | null;
  unit_converted: boolean;
}

export interface NotificationItem {
  notification_id: string;
  user_id: string | null;
  type: string;
  title: string;
  message: string;
  entity_type: string | null;
  entity_id: string | null;
  is_read: boolean;
  created_at: string;
}

export interface EmissionFactor {
  factor_id: string;
  standard: string;
  category: string;
  subcategory: string;
  activity_type: string;
  factor_value: number;
  unit: string;
  scope: string;
  region: string;
  country_code: string | null;
  grid_intensity_g_co2_kwh: number | null;
  valid_from: string;
  valid_to: string | null;
  version: string;
  description: string;
  is_active: boolean;
  radiative_forcing_multiplier: number;
  wtt_factor: number | null;
}

export interface Recommendation {
  id: string;
  category: string;
  action: string;
  description: string;
  estimated_saving_tco2e: number;
  estimated_cost_gbp: number | null;
  effort: string;
  impact: string;
  playbook: string;
}

export interface MLHealth {
  greenlight_loaded: boolean;
  greenlight_version: string | null;
  imputer_loaded: boolean;
  training_in_progress: boolean;
  last_trained_at: string | null;
  last_error: string | null;
}

export interface Document {
  doc_id: string;
  production_id: string;
  doc_type: string;
  filename: string;
  mime_type: string | null;
  file_size_bytes: number | null;
  ocr_status: string;
  extracted_confidence: number | null;
  extracted_data: any;
  review_status: string;
  uploaded_at: string;
  linked_event_ids: string[] | null;
}


