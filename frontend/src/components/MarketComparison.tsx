import React from 'react';
import { ComparisonSummary, Language, MarketRecord } from '../types';
import { translations } from '../i18n/translations';
import {
  TrendingUp,
  Download,
  Bell,
  Calculator,
  AlertTriangle,
  ExternalLink,
  Shield,
  Layers,
  MapPin,
  Calendar,
} from 'lucide-react';

interface MarketComparisonProps {
  records: MarketRecord[];
  summary: ComparisonSummary;
  language: Language;
  onOpenExportModal: () => void;
  onOpenAlertModal: (record?: MarketRecord) => void;
  onOpenProfitabilityModal: (record?: MarketRecord) => void;
}

export const MarketComparison: React.FC<MarketComparisonProps> = ({
  records,
  summary,
  language,
  onOpenExportModal,
  onOpenAlertModal,
  onOpenProfitabilityModal,
}) => {
  const t = translations[language];

  const usableRecords = records.filter(
    (r) => r.validation_status === 'valid' || r.validation_status === 'provisional'
  );
  const excludedRecords = records.filter(
    (r) => r.validation_status !== 'valid' && r.validation_status !== 'provisional'
  );

  return (
    <div className="comparison-container">
      {/* Top Action & Summary Bar */}
      <div className="comparison-header-panel panel">
        <div className="summary-title-row">
          <div>
            <h2 className="panel-title">{t.compTitle}</h2>
            <div className="price-range-banner">
              <span className="price-range-label">{t.compSummaryRange}</span>
              <span className="price-range-highlight">{summary.price_range_str}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="comparison-actions">
            <button
              className="btn-action-primary"
              onClick={onOpenExportModal}
              disabled={usableRecords.length === 0}
            >
              <Download size={16} />
              <span>{t.btnExportCsv}</span>
            </button>
            <button
              className="btn-action-secondary"
              onClick={() => onOpenAlertModal()}
            >
              <Bell size={16} />
              <span>{t.btnCreateAlert}</span>
            </button>
            <button
              className="btn-action-safety"
              onClick={() => onOpenProfitabilityModal(usableRecords[0])}
            >
              <Calculator size={16} />
              <span>{t.btnCalculateProceeds}</span>
            </button>
          </div>
        </div>

        {/* Profitability Safety Warning */}
        <div className="safety-warning-banner">
          <AlertTriangle size={20} color="#c62828" className="safety-icon" />
          <div className="safety-content">
            <strong>Mandatory Agricultural Safety Rule:</strong>
            <p className="safety-text">{t.safetyWarning}</p>
          </div>
        </div>

        {/* Metadata Indicators */}
        <div className="summary-pills-row">
          <div className="summary-pill">
            <span className="pill-label">{t.compUsableCount}</span>
            <strong className="pill-val success">{summary.usable_markets_count}</strong>
          </div>
          <div className="summary-pill">
            <span className="pill-label">{t.compExcludedCount}</span>
            <strong className="pill-val warning">{summary.excluded_markets_count}</strong>
          </div>
          <div className="summary-pill">
            <span className="pill-label">{t.compFreshnessLabel}</span>
            <strong className="pill-val">{summary.freshness_summary || 'Evaluated'}</strong>
          </div>
          <div className="summary-pill">
            <span className="pill-label">{t.compGradeNote}</span>
            <strong className="pill-val">{summary.grade_compatibility_note}</strong>
          </div>
        </div>
      </div>

      {/* Usable Market Cards */}
      <div className="market-cards-grid">
        {usableRecords.length === 0 ? (
          <div className="empty-state-card panel full-width">
            <p>No usable market records available. Check query filters or try a wider radius.</p>
          </div>
        ) : (
          usableRecords.map((r, idx) => (
            <div key={idx} className="market-card panel">
              <div className="market-card-top">
                <div className="market-title-area">
                  <h3 className="market-name">{r.market_name}</h3>
                  <div className="market-loc-row">
                    <MapPin size={14} color="#555" />
                    <span>{r.market_location}</span>
                    {r.distance_km != null && (
                      <span className="distance-badge">{r.distance_km} km away</span>
                    )}
                  </div>
                </div>
                <div className={`freshness-badge freshness-${r.freshness_category}`}>
                  {r.freshness_category === 'today' && t.freshnessToday}
                  {r.freshness_category === 'yesterday' && t.freshnessYesterday}
                  {r.freshness_category === 'older' && t.freshnessOlder}
                  {r.freshness_category === 'provisional' && 'Provisional'}
                </div>
              </div>

              {/* Price Row: Normalized Highlight */}
              <div className="price-spotlight-box">
                <div className="normalized-price-main">
                  <span className="norm-label">Normalized Price:</span>
                  <span className="norm-amount">
                    ₹{r.normalized_modal_price_per_kg?.toFixed(2) ?? 'N/A'}{' '}
                    <span className="norm-unit">/ kg</span>
                  </span>
                </div>
                {r.normalized_price_min_per_kg != null && r.normalized_price_max_per_kg != null && (
                  <span className="norm-range">
                    Range: ₹{r.normalized_price_min_per_kg.toFixed(2)} - ₹{r.normalized_price_max_per_kg.toFixed(2)} / kg
                  </span>
                )}
              </div>

              {/* Original Reported Price & Details */}
              <div className="reported-details-table">
                <div className="detail-row">
                  <span className="detail-key">Original Reported Price:</span>
                  <strong className="detail-val">
                    ₹{r.original_modal_price ?? 'N/A'} {r.original_unit}
                  </strong>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Crop & Grade:</span>
                  <span className="detail-val">
                    {r.crop} • <strong>{r.grade}</strong>
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Observation Date:</span>
                  <span className="detail-val date-val">
                    <Calendar size={13} /> {r.observation_date}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Data Provenance:</span>
                  <a
                    href={r.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="provenance-link"
                  >
                    <span>{r.source_id}</span>
                    <ExternalLink size={12} />
                  </a>
                </div>
              </div>

              {/* Card Footer Actions */}
              <div className="card-actions-row">
                <button
                  className="btn-card-action"
                  onClick={() => onOpenAlertModal(r)}
                >
                  <Bell size={14} /> Alert
                </button>
                <button
                  className="btn-card-action primary"
                  onClick={() => onOpenProfitabilityModal(r)}
                >
                  <Calculator size={14} /> Net Proceeds
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Excluded Records & Provenance Safeguards Panel */}
      {excludedRecords.length > 0 && (
        <div className="excluded-records-panel panel">
          <div className="panel-header">
            <h3 className="panel-title text-warning">{t.exclusionsTitle}</h3>
          </div>
          <div className="table-responsive">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Market</th>
                  <th>Reported Data</th>
                  <th>Observed Date</th>
                  <th>Exclusion Safeguard Reason</th>
                </tr>
              </thead>
              <tbody>
                {excludedRecords.map((ex, i) => (
                  <tr key={i} className="excluded-row">
                    <td>
                      <strong>{ex.market_name}</strong>
                      <div className="sub-loc">{ex.market_location}</div>
                    </td>
                    <td>
                      ₹{ex.original_modal_price} {ex.original_unit} ({ex.grade})
                    </td>
                    <td>{ex.observation_date}</td>
                    <td className="reason-cell">
                      <span className="exclusion-reason-tag">
                        {ex.exclusion_reason || 'Failed strict compatibility filter'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
