import {
  ActionExecutionResult,
  ActionPreview,
  AuditTrail,
  FarmerQuery,
  MarketRecord,
  PriceAlert,
  ProfitabilityCalculation,
  QueryResultsResponse,
  TestCaseResult,
} from '../types';

const API_BASE = '/api';

export const api = {
  // System config & health
  async getHealth(): Promise<{ status: string; service: string; data_provider_mode: string; gemini_api_configured: boolean }> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('Failed to reach backend health endpoint');
    return res.json();
  },

  async getConfig(): Promise<Record<string, any>> {
    const res = await fetch(`${API_BASE}/config`);
    if (!res.ok) throw new Error('Failed to fetch config');
    return res.json();
  },

  // Queries
  async createQuery(payload: {
    crop: string;
    grade: string;
    location: string;
    radius_km: number;
    language: string;
    transcript?: string;
    source_mode?: string;
  }): Promise<FarmerQuery> {
    const res = await fetch(`${API_BASE}/queries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to create farmer query');
    return res.json();
  },

  async runQuery(queryId: string): Promise<Record<string, any>> {
    const res = await fetch(`${API_BASE}/queries/${queryId}/run`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Failed to execute query pipeline for ${queryId}`);
    return res.json();
  },

  async getQueryResults(queryId: string): Promise<QueryResultsResponse> {
    const res = await fetch(`${API_BASE}/queries/${queryId}/results`);
    if (!res.ok) throw new Error(`Failed to fetch results for query ${queryId}`);
    return res.json();
  },

  async getQueryEvidence(queryId: string): Promise<AuditTrail> {
    const res = await fetch(`${API_BASE}/queries/${queryId}/evidence`);
    if (!res.ok) throw new Error(`Failed to fetch evidence for query ${queryId}`);
    return res.json();
  },

  async listQueries(): Promise<FarmerQuery[]> {
    const res = await fetch(`${API_BASE}/queries`);
    if (!res.ok) throw new Error('Failed to list queries');
    return res.json();
  },

  // Human-in-the-loop Actions
  async previewAction(payload: {
    query_id: string;
    action_type: 'export_comparison' | 'create_price_alert';
    payload: Record<string, any>;
  }): Promise<ActionPreview> {
    const res = await fetch(`${API_BASE}/actions/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to prepare action preview');
    }
    return res.json();
  },

  async approveAction(actionId: string, idempotencyKey: string): Promise<ActionExecutionResult> {
    const res = await fetch(`${API_BASE}/actions/${actionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ idempotency_key: idempotencyKey, approved: true }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to approve action');
    }
    return res.json();
  },

  async rejectAction(actionId: string): Promise<ActionExecutionResult> {
    const res = await fetch(`${API_BASE}/actions/${actionId}/reject`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to reject action');
    return res.json();
  },

  // Price Alerts
  async listAlerts(): Promise<PriceAlert[]> {
    const res = await fetch(`${API_BASE}/alerts`);
    if (!res.ok) throw new Error('Failed to list price alerts');
    return res.json();
  },

  async simulateAlertEvaluation(): Promise<{ alerts_triggered_count: number; triggered_details: any[] }> {
    const res = await fetch(`${API_BASE}/alerts/simulate-evaluate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to simulate alert evaluation');
    return res.json();
  },

  // Profitability Safety Calculation
  async calculateProfitability(payload: {
    market_name: string;
    selling_price_per_kg: number;
    quantity_kg: number;
    transport_cost_inr?: number | null;
    loading_charges_inr?: number;
    market_fees_inr?: number;
    packaging_costs_inr?: number;
  }): Promise<ProfitabilityCalculation> {
    const res = await fetch(`${API_BASE}/markets/profitability`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to calculate profitability');
    return res.json();
  },

  // Official Test Suite
  async listTests(): Promise<TestCaseResult[]> {
    const res = await fetch(`${API_BASE}/tests`);
    if (!res.ok) throw new Error('Failed to load test suite');
    return res.json();
  },

  async runSingleTest(testCaseId: string): Promise<TestCaseResult> {
    const res = await fetch(`${API_BASE}/tests/${testCaseId}/run`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error(`Failed to execute ${testCaseId}`);
    return res.json();
  },

  async runAllTests(): Promise<TestCaseResult[]> {
    const res = await fetch(`${API_BASE}/tests/run-all`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to execute all test cases');
    return res.json();
  },
};
