import React, { useState } from 'react';
import { Language, PriceAlert } from '../types';
import { translations } from '../i18n/translations';
import { api } from '../services/api';
import { Bell, Play, CheckCircle2, AlertCircle, Clock, ShieldCheck, Tag } from 'lucide-react';

interface PriceAlertsProps {
  alerts: PriceAlert[];
  language: Language;
  onOpenCreateAlertModal: () => void;
  onRefreshAlerts: () => void;
}

export const PriceAlerts: React.FC<PriceAlertsProps> = ({
  alerts,
  language,
  onOpenCreateAlertModal,
  onRefreshAlerts,
}) => {
  const t = translations[language];

  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<string | null>(null);

  const handleSimulate = async () => {
    setIsSimulating(true);
    setSimulationResult(null);
    try {
      const res = await api.simulateAlertEvaluation();
      setSimulationResult(
        `Simulation evaluated against recent mandi arrivals. Triggered alerts: ${res.alerts_triggered_count}`
      );
      onRefreshAlerts();
    } catch (e: any) {
      setSimulationResult(`Simulation failed: ${e.message}`);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="alerts-container panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">{t.alertsTitle}</h2>
          <p className="panel-subtitle">{t.alertsSubtitle}</p>
        </div>
        <div className="alerts-header-actions">
          <button className="btn-secondary-medium" onClick={handleSimulate} disabled={isSimulating}>
            <Play size={16} />
            <span>{isSimulating ? 'Evaluating...' : t.btnSimulateArrivals}</span>
          </button>
          <button className="btn-primary-medium" onClick={onOpenCreateAlertModal}>
            <Bell size={16} />
            <span>+ Set New Alert</span>
          </button>
        </div>
      </div>

      {/* Simulation Result notice */}
      {simulationResult && (
        <div className="simulation-notice-box">
          <CheckCircle2 size={18} color="#2e7d32" />
          <span>{simulationResult}</span>
        </div>
      )}

      {/* Demo notification disclosure */}
      <div className="demo-notice-banner">
        <ShieldCheck size={16} />
        <span>
          Transparency Notice: All price alert evaluations in this demo mode are simulated in-app.
          No unauthorized SMS or WhatsApp messages are dispatched.
        </span>
      </div>

      {/* Alerts List */}
      <div className="alerts-grid">
        {alerts.length === 0 ? (
          <div className="empty-alerts-card">
            <Bell size={36} color="#aaa" />
            <p>No price alerts set yet. Click '+ Set New Alert' to configure a target price alert.</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.alert_id} className={`alert-card status-${alert.status}`}>
              <div className="alert-card-top">
                <div className="alert-crop-info">
                  <h3 className="alert-crop-name">{alert.crop}</h3>
                  <span className="alert-market-name">{alert.market}</span>
                </div>
                <div className="alert-status-group">
                  <span className={`alert-status-badge ${alert.status}`}>
                    {alert.status.toUpperCase()}
                  </span>
                  <span className="simulated-pill">Simulated</span>
                </div>
              </div>

              <div className="alert-condition-row">
                <span className="condition-label">Condition:</span>
                <strong className="condition-highlight">
                  Trigger when price goes {alert.threshold_direction} ₹{alert.target_price.toFixed(2)} / {alert.unit}
                </strong>
              </div>

              {/* Evaluation History */}
              <div className="alert-history-area">
                <div className="history-header">
                  <Clock size={12} />
                  <span>Evaluation Log:</span>
                </div>
                <ul className="history-list">
                  {alert.evaluation_history.map((ev, i) => (
                    <li key={i} className="history-item">
                      <span className="history-time">{new Date(ev.timestamp).toLocaleTimeString()}:</span>{' '}
                      <span className="history-msg">{ev.message}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="alert-card-footer">
                <span className="alert-id-tag">ID: {alert.alert_id}</span>
                <span className="alert-created-time">
                  Created: {new Date(alert.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
