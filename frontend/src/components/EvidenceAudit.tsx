import React from 'react';
import { AuditTrail, Language } from '../types';
import { translations } from '../i18n/translations';
import {
  ShieldCheck,
  CheckCircle,
  Clock,
  Terminal,
  Layers,
  ArrowRight,
  ExternalLink,
  Cpu,
} from 'lucide-react';

interface EvidenceAuditProps {
  evidence: AuditTrail | null;
  language: Language;
}

export const EvidenceAudit: React.FC<EvidenceAuditProps> = ({ evidence, language }) => {
  const t = translations[language];

  if (!evidence) {
    return (
      <div className="panel empty-evidence-panel">
        <ShieldCheck size={40} color="#aaa" />
        <p>No audit trail selected. Run a farmer query to inspect live tool execution and audit logs.</p>
      </div>
    );
  }

  return (
    <div className="evidence-container">
      {/* Overview header */}
      <div className="evidence-header-panel panel">
        <div className="evidence-title-row">
          <div>
            <h2 className="panel-title">{t.evidenceTitle}</h2>
            <p className="panel-subtitle">{t.evidenceSubtitle}</p>
          </div>
          <div className="audit-ids-group">
            <span className="audit-id-pill">Query ID: {evidence.query_id}</span>
            <span className="audit-id-pill">Execution ID: {evidence.execution_id}</span>
            <span className={`tag-mode ${evidence.source_mode}`}>Mode: {evidence.source_mode}</span>
          </div>
        </div>

        {/* Verification Checks */}
        <div className="verification-checks-bar">
          <span className="vc-label">Independent Pipeline Integrity Checks:</span>
          <div className="vc-pills-row">
            {evidence.verification_checks.map((vc, i) => (
              <div key={i} className="vc-pill-item">
                <CheckCircle size={15} color="#2e7d32" />
                <span>{vc.check}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dual Column: Planning Steps & Tool Invocations */}
      <div className="audit-grid-dual">
        {/* Planning Steps */}
        <div className="panel planning-panel">
          <div className="panel-header">
            <h3 className="panel-title">
              <Cpu size={18} /> Orchestrator Planning Steps
            </h3>
          </div>
          <ol className="planning-steps-list">
            {evidence.planning_steps.map((step, idx) => (
              <li key={idx} className="planning-step-item">
                <span className="step-num">{idx + 1}</span>
                <span className="step-desc">{step}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Tool Events Timeline */}
        <div className="panel tool-events-panel">
          <div className="panel-header">
            <h3 className="panel-title">
              <Terminal size={18} /> Tool Execution Timeline
            </h3>
          </div>
          <div className="timeline-container">
            {evidence.tool_events.map((evt, idx) => (
              <div key={idx} className="timeline-event-card">
                <div className="event-header-row">
                  <span className="tool-name-badge">
                    <code>{evt.tool}</code>
                  </span>
                  <span className="tool-duration">
                    <Clock size={12} /> {evt.duration_ms} ms
                  </span>
                </div>
                <div className="event-json-box">
                  <details>
                    <summary>View Tool Inputs & Outputs</summary>
                    <div className="json-diff-view">
                      <div className="json-half">
                        <span className="json-subhead">Input Parameters:</span>
                        <pre>{JSON.stringify(evt.inputs, null, 2)}</pre>
                      </div>
                      <div className="json-half">
                        <span className="json-subhead">Tool Result:</span>
                        <pre>{JSON.stringify(evt.outputs, null, 2)}</pre>
                      </div>
                    </div>
                  </details>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Normalization & Exclusions Decisions Table */}
      <div className="panel normalization-decisions-panel">
        <div className="panel-header">
          <h3 className="panel-title">
            <Layers size={18} /> Price Normalization & Provenance Audit
          </h3>
        </div>
        <div className="table-responsive">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Market</th>
                <th>Original Reported Price</th>
                <th>Normalized INR/kg</th>
                <th>Observed Date</th>
                <th>Freshness</th>
                <th>Validation Status</th>
                <th>Source Provenance</th>
              </tr>
            </thead>
            <tbody>
              {evidence.normalization_decisions.map((item, idx) => (
                <tr key={idx}>
                  <td>
                    <strong>{item.market}</strong>
                  </td>
                  <td>
                    <code>{item.original}</code>
                  </td>
                  <td>
                    <strong className="text-success">{item.normalized_kg}</strong>
                  </td>
                  <td>{item.observation_date}</td>
                  <td>
                    <span className={`freshness-badge freshness-${item.freshness}`}>
                      {item.freshness}
                    </span>
                  </td>
                  <td>
                    <span className={`status-pill status-${item.validation_status}`}>
                      {item.validation_status}
                    </span>
                    {item.exclusion_reason && (
                      <div className="sub-reason">{item.exclusion_reason}</div>
                    )}
                  </td>
                  <td>
                    <a
                      href={item.source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="provenance-link"
                    >
                      <span>Public Portal</span>
                      <ExternalLink size={12} />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
