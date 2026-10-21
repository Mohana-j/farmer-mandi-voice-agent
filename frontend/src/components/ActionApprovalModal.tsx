import React, { useState } from 'react';
import { ActionExecutionResult, ActionPreview, Language } from '../types';
import { translations } from '../i18n/translations';
import { api } from '../services/api';
import {
  ShieldAlert,
  CheckCircle,
  XCircle,
  FileSpreadsheet,
  Bell,
  RefreshCw,
  Hash,
  Download,
} from 'lucide-react';

interface ActionApprovalModalProps {
  preview: ActionPreview;
  language: Language;
  onClose: () => void;
  onExecutionComplete: (result: ActionExecutionResult) => void;
}

export const ActionApprovalModal: React.FC<ActionApprovalModalProps> = ({
  preview,
  language,
  onClose,
  onExecutionComplete,
}) => {
  const t = translations[language];

  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<ActionExecutionResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleApprove = async () => {
    setIsExecuting(true);
    setErrorMsg(null);
    try {
      const res = await api.approveAction(preview.action_id, preview.idempotency_key);
      setResult(res);
      onExecutionComplete(res);
    } catch (e: any) {
      setErrorMsg(e.message || 'Execution error');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleReject = async () => {
    setIsExecuting(true);
    setErrorMsg(null);
    try {
      const res = await api.rejectAction(preview.action_id);
      setResult(res);
      onExecutionComplete(res);
    } catch (e: any) {
      setErrorMsg(e.message || 'Rejection error');
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div className="modal-icon-group">
            <ShieldAlert size={26} color="#2e7d32" />
            <div>
              <h3 className="modal-title">{t.modalApprovalTitle}</h3>
              <p className="modal-subtitle">{t.modalApprovalSubtitle}</p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          {/* Action Spec Details */}
          <div className="spec-table">
            <div className="spec-row">
              <span className="spec-label">{t.modalActionType}</span>
              <span className="spec-value action-type-tag">
                {preview.action_type === 'export_comparison' ? (
                  <>
                    <FileSpreadsheet size={15} /> Export Market CSV
                  </>
                ) : (
                  <>
                    <Bell size={15} /> Set Price Alert
                  </>
                )}
              </span>
            </div>
            <div className="spec-row">
              <span className="spec-label">{t.modalActionId}</span>
              <span className="spec-value mono">{preview.action_id}</span>
            </div>
            <div className="spec-row">
              <span className="spec-label">{t.modalIdempotencyKey}</span>
              <span className="spec-value mono idempotency-tag">
                <Hash size={13} /> {preview.idempotency_key}
              </span>
            </div>
            <div className="spec-row">
              <span className="spec-label">{t.modalDestination}</span>
              <span className="spec-value mono">{preview.destination}</span>
            </div>
            <div className="spec-row">
              <span className="spec-label">{t.modalSummary}</span>
              <span className="spec-value">{preview.summary_of_changes}</span>
            </div>
          </div>

          {/* Error notice */}
          {errorMsg && (
            <div className="modal-error-alert">
              <XCircle size={18} />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Verification Result Display */}
          {result && (
            <div
              className={`verification-result-box ${
                result.verification_status === 'verified_success' ? 'success' : 'rejected'
              }`}
            >
              <div className="result-header">
                {result.verification_status === 'verified_success' ? (
                  <CheckCircle size={20} color="#2e7d32" />
                ) : (
                  <XCircle size={20} color="#c62828" />
                )}
                <strong>
                  {result.verification_status === 'verified_success'
                    ? 'Verified & Executed Successfully'
                    : 'Action Rejected / Left Unexecuted'}
                </strong>
              </div>
              <p className="result-message">{result.message}</p>

              {result.verification_details && (
                <div className="verification-details-pane">
                  <span className="vd-title">Independent Post-Execution Evidence:</span>
                  <pre className="vd-json">
                    {JSON.stringify(result.verification_details, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer Controls */}
        <div className="modal-footer">
          {!result ? (
            <>
              <button
                className="btn-reject"
                onClick={handleReject}
                disabled={isExecuting}
              >
                <XCircle size={16} />
                <span>{t.btnReject}</span>
              </button>
              <button
                className="btn-approve"
                onClick={handleApprove}
                disabled={isExecuting}
              >
                {isExecuting ? (
                  <>
                    <RefreshCw size={16} className="spin" />
                    <span>Executing & Verifying...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle size={16} />
                    <span>{t.btnApprove}</span>
                  </>
                )}
              </button>
            </>
          ) : (
            <button className="btn-done" onClick={onClose}>
              {t.btnDone}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
