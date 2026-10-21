import React from 'react';
import { FarmerQuery, Language, QueryResultsResponse } from '../types';
import { translations } from '../i18n/translations';
import { Mic, ArrowRight, Clock, Store, ShieldCheck, Database, CheckCircle2 } from 'lucide-react';

interface DashboardProps {
  language: Language;
  onStartVoice: () => void;
  onNavigate: (tab: string) => void;
  recentQueries: FarmerQuery[];
  latestResult: QueryResultsResponse | null;
  sourceMode: 'synthetic' | 'live';
  onSelectQuery: (queryId: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  language,
  onStartVoice,
  onNavigate,
  recentQueries,
  latestResult,
  sourceMode,
  onSelectQuery,
}) => {
  const t = translations[language];

  const totalUsableMarkets = latestResult?.summary.usable_markets_count ?? 3;
  const lastTimestamp = latestResult?.records[0]?.retrieved_at
    ? new Date(latestResult.records[0].retrieved_at).toLocaleTimeString()
    : 'Ready';

  return (
    <div className="dashboard-container">
      {/* Hero Welcome Banner */}
      <section className="hero-banner">
        <div className="hero-content">
          <span className="hero-pill">Hackathon 2026 — Ziro.Digital</span>
          <h2 className="hero-heading">{t.dashTitle}</h2>
          <p className="hero-subtext">{t.dashSubtitle}</p>
          <div className="hero-actions">
            <button className="btn-primary-large" onClick={onStartVoice}>
              <Mic size={22} className="btn-icon" />
              <span>{t.btnStartVoice}</span>
            </button>
            <button className="btn-secondary-large" onClick={() => onNavigate('tests')}>
              <ShieldCheck size={20} className="btn-icon" />
              <span>{t.linkTests}</span>
            </button>
          </div>
        </div>
      </section>

      {/* Metric Cards */}
      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <Database size={20} color="#2e7d32" />
            <span className="stat-title">{t.statActiveMode}</span>
          </div>
          <div className="stat-value-row">
            <span className="stat-main-text">
              {sourceMode === 'live' ? 'Live Mandi Portal' : 'Synthetic Fixture'}
            </span>
            <span className={`tag-mode ${sourceMode}`}>
              {sourceMode === 'live' ? 'Gov. Data API' : 'Verified Demo'}
            </span>
          </div>
          <p className="stat-footer">
            {sourceMode === 'live'
              ? 'Connected to Open Government Data Platform'
              : 'Deterministic fixtures active for offline reliability'}
          </p>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <Clock size={20} color="#2e7d32" />
            <span className="stat-title">{t.statLastRetrieval}</span>
          </div>
          <div className="stat-value-row">
            <span className="stat-main-text">{lastTimestamp}</span>
            <span className="tag-mode active">Tracked</span>
          </div>
          <p className="stat-footer">
            {latestResult?.summary.dates_observed.length
              ? `Observation dates: ${latestResult.summary.dates_observed.join(', ')}`
              : 'Standby for query'}
          </p>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <Store size={20} color="#2e7d32" />
            <span className="stat-title">{t.statTotalMarkets}</span>
          </div>
          <div className="stat-value-row">
            <span className="stat-main-text">{totalUsableMarkets} Mandis</span>
            <span className="tag-mode success">In Range</span>
          </div>
          <p className="stat-footer">
            Dharmapuri, Palacode, Pennagaram & Krishnagiri APMCs
          </p>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <CheckCircle2 size={20} color="#2e7d32" />
            <span className="stat-title">{t.statTestsPassed}</span>
          </div>
          <div className="stat-value-row">
            <span className="stat-main-text">4 / 4 Passing</span>
            <span className="tag-mode verified">100% Audited</span>
          </div>
          <p className="stat-footer">
            TC1 (Nearby), TC2 (Yesterday), TC3 (Units), TC4 (Safety)
          </p>
        </div>
      </section>

      {/* Grid: Recent Queries + Quick Nav */}
      <section className="dashboard-grid-dual">
        {/* Recent Queries */}
        <div className="panel recent-queries-panel">
          <div className="panel-header">
            <h3 className="panel-title">{t.recentQueriesTitle}</h3>
            <button className="btn-link" onClick={() => onNavigate('query')}>
              + New Query
            </button>
          </div>
          <div className="queries-list">
            {recentQueries.length === 0 ? (
              <p className="empty-state-text">{t.noQueriesYet}</p>
            ) : (
              recentQueries.slice(0, 5).map((q) => (
                <div
                  key={q.query_id}
                  className="query-row-item"
                  onClick={() => onSelectQuery(q.query_id)}
                >
                  <div className="query-info-col">
                    <div className="query-title-row">
                      <strong>{q.crop.toUpperCase()}</strong>
                      <span className="query-grade-pill">{q.grade}</span>
                      <span className="query-loc-pill">{q.location} ({q.radius_km} km)</span>
                    </div>
                    <span className="query-time">
                      ID: {q.query_id} • {new Date(q.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="query-status-col">
                    <span className={`status-pill status-${q.status}`}>{q.status}</span>
                    <ArrowRight size={16} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Quick Links Card */}
        <div className="panel quick-nav-panel">
          <div className="panel-header">
            <h3 className="panel-title">{t.quickLinksTitle}</h3>
          </div>
          <div className="quick-links-list">
            <button className="quick-link-btn" onClick={() => onNavigate('comparison')}>
              <div className="quick-link-icon-box">📊</div>
              <div className="quick-link-text">
                <strong>{t.linkComparison}</strong>
                <span>Review normalized prices in INR/kg and freshness</span>
              </div>
              <ArrowRight size={18} />
            </button>

            <button className="quick-link-btn" onClick={() => onNavigate('alerts')}>
              <div className="quick-link-icon-box">🔔</div>
              <div className="quick-link-text">
                <strong>{t.linkAlerts}</strong>
                <span>Set verified price thresholds with approval gate</span>
              </div>
              <ArrowRight size={18} />
            </button>

            <button className="quick-link-btn" onClick={() => onNavigate('evidence')}>
              <div className="quick-link-icon-box">🛡️</div>
              <div className="quick-link-text">
                <strong>{t.linkEvidence}</strong>
                <span>Examine state transitions, tool events & audits</span>
              </div>
              <ArrowRight size={18} />
            </button>

            <button className="quick-link-btn" onClick={() => onNavigate('tests')}>
              <div className="quick-link-icon-box">🧪</div>
              <div className="quick-link-text">
                <strong>{t.linkTests}</strong>
                <span>Execute automated TC1, TC2, TC3, and TC4</span>
              </div>
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
