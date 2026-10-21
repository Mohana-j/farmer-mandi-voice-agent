import React, { useEffect, useState } from 'react';
import {
  ActionExecutionResult,
  ActionPreview,
  AuditTrail,
  FarmerQuery,
  Language,
  MarketRecord,
  PriceAlert,
  QueryResultsResponse,
  TestCaseResult,
} from './types';
import { api } from './services/api';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { QueryForm } from './components/QueryForm';
import { VoiceAnswer } from './components/VoiceAnswer';
import { MarketComparison } from './components/MarketComparison';
import { ActionApprovalModal } from './components/ActionApprovalModal';
import { ProfitabilityModal } from './components/ProfitabilityModal';
import { PriceAlerts } from './components/PriceAlerts';
import { EvidenceAudit } from './components/EvidenceAudit';
import { TestDashboard } from './components/TestDashboard';
import './App.css';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [language, setLanguage] = useState<Language>('en');
  const [sourceMode, setSourceMode] = useState<'synthetic' | 'live'>('synthetic');
  const [isHealthy, setIsHealthy] = useState(false);

  // Data states
  const [recentQueries, setRecentQueries] = useState<FarmerQuery[]>([]);
  const [activeQueryId, setActiveQueryId] = useState<string | null>(null);
  const [latestResult, setLatestResult] = useState<QueryResultsResponse | null>(null);
  const [evidence, setEvidence] = useState<AuditTrail | null>(null);
  const [alerts, setAlerts] = useState<PriceAlert[]>([]);
  const [testCases, setTestCases] = useState<TestCaseResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Modals
  const [actionPreview, setActionPreview] = useState<ActionPreview | null>(null);
  const [profitabilityRecord, setProfitabilityRecord] = useState<MarketRecord | null>(null);
  const [isProfitModalOpen, setIsProfitModalOpen] = useState(false);

  // Initial startup loader
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const health = await api.getHealth();
      setIsHealthy(health.status === 'healthy');
      setSourceMode((health.data_provider_mode as 'synthetic' | 'live') || 'synthetic');

      // Load queries
      const qList = await api.listQueries();
      setRecentQueries(qList);
      if (qList.length > 0) {
        const topQ = qList[0];
        setActiveQueryId(topQ.query_id);
        if (topQ.status === 'completed') {
          const res = await api.getQueryResults(topQ.query_id);
          setLatestResult(res);
          const ev = await api.getQueryEvidence(topQ.query_id);
          setEvidence(ev);
        }
      }

      // Load alerts
      const aList = await api.listAlerts();
      setAlerts(aList);

      // Load test cases
      const tList = await api.listTests();
      setTestCases(tList);
    } catch (e) {
      console.error('Initialization error:', e);
    }
  };

  const handleSelectQuery = async (queryId: string) => {
    setActiveQueryId(queryId);
    try {
      const res = await api.getQueryResults(queryId);
      setLatestResult(res);
      const ev = await api.getQueryEvidence(queryId);
      setEvidence(ev);
      setCurrentTab('comparison');
    } catch (e) {
      console.error('Failed to load selected query results:', e);
    }
  };

  const handleQuerySubmit = async (params: {
    crop: string;
    grade: string;
    location: string;
    radius_km: number;
    language: Language;
    transcript?: string;
  }) => {
    setIsSearching(true);
    try {
      // 1. Create query
      const created = await api.createQuery({
        ...params,
        source_mode: sourceMode,
      });
      setActiveQueryId(created.query_id);

      // 2. Run agent pipeline
      await api.runQuery(created.query_id);

      // 3. Fetch results & evidence
      const res = await api.getQueryResults(created.query_id);
      setLatestResult(res);
      const ev = await api.getQueryEvidence(created.query_id);
      setEvidence(ev);

      // Refresh recent queries
      const qList = await api.listQueries();
      setRecentQueries(qList);

      // Switch to comparison tab to see results
      setCurrentTab('comparison');
    } catch (e: any) {
      alert(`Query failed: ${e.message}`);
    } finally {
      setIsSearching(false);
    }
  };

  const handleOpenExportModal = async () => {
    if (!activeQueryId) return;
    try {
      const preview = await api.previewAction({
        query_id: activeQueryId,
        action_type: 'export_comparison',
        payload: {},
      });
      setActionPreview(preview);
    } catch (e: any) {
      alert(`Failed to prepare export preview: ${e.message}`);
    }
  };

  const handleOpenAlertModal = async (record?: MarketRecord) => {
    const crop = record?.crop || latestResult?.query.crop || 'Tomato';
    const market = record?.market_name || 'Dharmapuri Regulated Market';
    const price = record?.normalized_modal_price_per_kg || 22.0;

    try {
      const preview = await api.previewAction({
        query_id: activeQueryId || 'q-direct',
        action_type: 'create_price_alert',
        payload: {
          crop,
          market,
          target_price: price,
          unit: 'INR/kg',
          threshold_direction: 'below',
        },
      });
      setActionPreview(preview);
    } catch (e: any) {
      alert(`Failed to prepare price alert preview: ${e.message}`);
    }
  };

  const handleExecutionComplete = async (res: ActionExecutionResult) => {
    // Refresh alerts and evidence
    const aList = await api.listAlerts();
    setAlerts(aList);
    if (activeQueryId) {
      const ev = await api.getQueryEvidence(activeQueryId);
      setEvidence(ev);
    }
  };

  return (
    <div className="app-layout">
      <Header
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        language={language}
        setLanguage={setLanguage}
        sourceMode={sourceMode}
        isHealthy={isHealthy}
      />

      <main className="main-content">
        {currentTab === 'dashboard' && (
          <Dashboard
            language={language}
            onStartVoice={() => setCurrentTab('query')}
            onNavigate={setCurrentTab}
            recentQueries={recentQueries}
            latestResult={latestResult}
            sourceMode={sourceMode}
            onSelectQuery={handleSelectQuery}
          />
        )}

        {currentTab === 'query' && (
          <div className="query-view-stack">
            <QueryForm
              language={language}
              onSubmitQuery={handleQuerySubmit}
              isSearching={isSearching}
              activeQueryId={activeQueryId}
            />

            {latestResult && (
              <VoiceAnswer
                answerEn={latestResult.voice_answer_en}
                answerTa={latestResult.voice_answer_ta}
                language={language}
                observationDates={latestResult.summary.dates_observed}
                sourceNames={latestResult.summary.source_names}
                isYesterdayData={
                  latestResult.records.length > 0 &&
                  latestResult.records.every((r) => r.freshness_category === 'yesterday')
                }
                isStaleOrUncertain={latestResult.summary.grade_compatibility_note.includes('provisional')}
              />
            )}
          </div>
        )}

        {currentTab === 'comparison' && (
          <div className="comparison-view-stack">
            {latestResult ? (
              <>
                <VoiceAnswer
                  answerEn={latestResult.voice_answer_en}
                  answerTa={latestResult.voice_answer_ta}
                  language={language}
                  observationDates={latestResult.summary.dates_observed}
                  sourceNames={latestResult.summary.source_names}
                  isYesterdayData={
                    latestResult.records.length > 0 &&
                    latestResult.records.every((r) => r.freshness_category === 'yesterday')
                  }
                  isStaleOrUncertain={latestResult.summary.grade_compatibility_note.includes('provisional')}
                />
                <MarketComparison
                  records={latestResult.records}
                  summary={latestResult.summary}
                  language={language}
                  onOpenExportModal={handleOpenExportModal}
                  onOpenAlertModal={handleOpenAlertModal}
                  onOpenProfitabilityModal={(rec) => {
                    setProfitabilityRecord(rec || null);
                    setIsProfitModalOpen(true);
                  }}
                />
              </>
            ) : (
              <div className="panel empty-state-card">
                <h3>No comparison available</h3>
                <p>Please submit a farmer voice or text query to view mandi price comparisons.</p>
                <button className="btn-primary-medium" onClick={() => setCurrentTab('query')}>
                  Ask Question
                </button>
              </div>
            )}
          </div>
        )}

        {currentTab === 'alerts' && (
          <PriceAlerts
            alerts={alerts}
            language={language}
            onOpenCreateAlertModal={() => handleOpenAlertModal()}
            onRefreshAlerts={async () => {
              const aList = await api.listAlerts();
              setAlerts(aList);
            }}
          />
        )}

        {currentTab === 'evidence' && (
          <EvidenceAudit evidence={evidence} language={language} />
        )}

        {currentTab === 'tests' && (
          <TestDashboard
            testCases={testCases}
            language={language}
            onRefreshTests={async () => {
              const tList = await api.listTests();
              setTestCases(tList);
            }}
          />
        )}
      </main>

      {/* Action Approval Modal */}
      {actionPreview && (
        <ActionApprovalModal
          preview={actionPreview}
          language={language}
          onClose={() => setActionPreview(null)}
          onExecutionComplete={handleExecutionComplete}
        />
      )}

      {/* Profitability Estimator Modal */}
      {isProfitModalOpen && (
        <ProfitabilityModal
          marketRecord={profitabilityRecord || undefined}
          language={language}
          onClose={() => setIsProfitModalOpen(false)}
        />
      )}
    </div>
  );
};
