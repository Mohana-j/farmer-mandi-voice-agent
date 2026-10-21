export type Language = 'en' | 'ta';

export interface FarmerQuery {
  id: number;
  query_id: string;
  crop: string;
  grade: string;
  location: string;
  radius_km: number;
  language: Language;
  transcript?: string;
  source_mode: 'synthetic' | 'live';
  status: 'pending' | 'completed' | 'failed' | 'clarification_needed';
  voice_response_en?: string;
  voice_response_ta?: string;
  clarification_message?: string;
  created_at: string;
  updated_at: string;
}

export interface MarketRecord {
  id?: number;
  query_id: string;
  source_id: string;
  source_url: string;
  source_record_id: string;
  market_name: string;
  market_location: string;
  distance_km?: number | null;
  crop: string;
  grade: string;
  original_price_min?: number | null;
  original_price_max?: number | null;
  original_modal_price?: number | null;
  original_unit: string;
  normalized_price_min_per_kg?: number | null;
  normalized_price_max_per_kg?: number | null;
  normalized_modal_price_per_kg?: number | null;
  observation_date: string;
  freshness_category: 'today' | 'yesterday' | 'older' | 'unknown' | 'provisional';
  retrieved_at: string;
  data_mode: 'synthetic' | 'live';
  validation_status: 'valid' | 'provisional' | 'incompatible_grade' | 'unknown_unit' | 'outside_radius' | 'stale';
  exclusion_reason?: string | null;
}

export interface ComparisonSummary {
  lowest_price_per_kg?: number | null;
  highest_price_per_kg?: number | null;
  price_range_str: string;
  usable_markets_count: number;
  excluded_markets_count: number;
  all_same_date: boolean;
  dates_observed: string[];
  freshness_summary: string;
  grade_compatibility_note: string;
  profitability_disclaimer: string;
  source_names: string[];
}

export interface QueryResultsResponse {
  query: FarmerQuery;
  records: MarketRecord[];
  summary: ComparisonSummary;
  voice_answer_en: string;
  voice_answer_ta: string;
  execution_id: string;
  source_mode: 'synthetic' | 'live';
}

export interface ActionPreview {
  action_id: string;
  query_id: string;
  action_type: 'export_comparison' | 'create_price_alert';
  action_version: number;
  idempotency_key: string;
  destination: string;
  summary_of_changes: string;
  preview_data: Record<string, any>;
  approval_status: 'pending' | 'approved' | 'rejected';
}

export interface ActionExecutionResult {
  action_id: string;
  idempotency_key: string;
  approval_status: string;
  execution_status: string;
  verification_status: string;
  verification_details?: Record<string, any>;
  message: string;
}

export interface PriceAlert {
  id: number;
  alert_id: string;
  query_id?: string;
  crop: string;
  market: string;
  target_price: number;
  unit: string;
  threshold_direction: 'above' | 'below';
  status: 'active' | 'triggered' | 'paused' | 'cancelled';
  is_simulated: boolean;
  created_at: string;
  triggered_at?: string | null;
  evaluation_history: Array<{
    timestamp: string;
    status: string;
    message: string;
    evaluated_price?: number;
    target_price?: number;
  }>;
}

export interface AuditEvent {
  tool: string;
  inputs: any;
  outputs: any;
  duration_ms: number;
  timestamp: string;
}

export interface AuditTrail {
  query_id: string;
  execution_id: string;
  source_mode: string;
  records_count: number;
  tool_events: AuditEvent[];
  planning_steps: string[];
  normalization_decisions: Array<{
    market: string;
    original: string;
    normalized_kg: string;
    observation_date: string;
    freshness: string;
    validation_status: string;
    exclusion_reason?: string;
    source_url: string;
  }>;
  actions_taken: Array<{
    action_id: string;
    type: string;
    approval_status: string;
    execution_status: string;
    verification_status: string;
  }>;
  verification_checks: Array<{
    check: string;
    passed: boolean;
  }>;
}

export interface TestCaseResult {
  test_case_id: string;
  title: string;
  status: 'passed' | 'failed';
  input_fixture: Record<string, any>;
  expected_behavior: Record<string, any>;
  actual_output: Record<string, any>;
  assertions_passed: string[];
  assertions_failed: string[];
  evidence: Record<string, any>;
  executed_at: string;
  duration_ms: number;
}

export interface ProfitabilityCalculation {
  is_calculable: boolean;
  market_name: string;
  disclaimer: string;
  gross_revenue_inr?: number | null;
  total_estimated_costs_inr?: number | null;
  estimated_net_proceeds_inr?: number | null;
  cost_breakdown?: {
    transport_cost: number;
    loading_charges: number;
    market_fees: number;
    packaging_costs: number;
    other_expenses: number;
  } | null;
  safety_note?: string;
}
