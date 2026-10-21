import React, { useState } from 'react';
import { Language, MarketRecord, ProfitabilityCalculation } from '../types';
import { translations } from '../i18n/translations';
import { api } from '../services/api';
import { Calculator, AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface ProfitabilityModalProps {
  marketRecord?: MarketRecord;
  language: Language;
  onClose: () => void;
}

export const ProfitabilityModal: React.FC<ProfitabilityModalProps> = ({
  marketRecord,
  language,
  onClose,
}) => {
  const t = translations[language];

  const [marketName, setMarketName] = useState(
    marketRecord?.market_name || 'Dharmapuri Regulated Market'
  );
  const [sellingPrice, setSellingPrice] = useState(
    marketRecord?.normalized_modal_price_per_kg || 22.0
  );
  const [quantityKg, setQuantityKg] = useState(1000);
  const [transportCost, setTransportCost] = useState<string>(''); // empty by default to show strict safety check
  const [loadingCharges, setLoadingCharges] = useState(300);
  const [marketFees, setMarketFees] = useState(250);
  const [packagingCosts, setPackagingCosts] = useState(200);

  const [calcResult, setCalcResult] = useState<ProfitabilityCalculation | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const handleCalculate = async () => {
    setIsCalculating(true);
    try {
      const transportNum = transportCost.trim() === '' ? null : Number(transportCost);
      const res = await api.calculateProfitability({
        market_name: marketName,
        selling_price_per_kg: Number(sellingPrice),
        quantity_kg: Number(quantityKg),
        transport_cost_inr: transportNum,
        loading_charges_inr: Number(loadingCharges),
        market_fees_inr: Number(marketFees),
        packaging_costs_inr: Number(packagingCosts),
      });
      setCalcResult(res);
    } catch (e: any) {
      console.error(e);
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div className="modal-icon-group">
            <Calculator size={26} color="#2e7d32" />
            <div>
              <h3 className="modal-title">Farmer Net Proceeds & Cost Estimator</h3>
              <p className="modal-subtitle">Strict Safety Rule: Gross price is NOT guaranteed profit.</p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="modal-body">
          {/* Initial Safety Notice */}
          <div className="safety-warning-banner">
            <AlertTriangle size={18} color="#c62828" />
            <div>
              <strong>Agricultural Decision Rule:</strong>
              <p>A higher selling price at a distant mandi may be completely wiped out by vehicle hire, diesel, toll fees, and loading charges.</p>
            </div>
          </div>

          {/* Input fields */}
          <div className="profit-inputs-grid">
            <div className="form-field">
              <label className="field-label">Selected Mandi</label>
              <input
                type="text"
                className="input-text"
                value={marketName}
                onChange={(e) => setMarketName(e.target.value)}
              />
            </div>

            <div className="form-field">
              <label className="field-label">Expected Price (INR / kg)</label>
              <input
                type="number"
                step="0.5"
                className="input-text"
                value={sellingPrice}
                onChange={(e) => setSellingPrice(Number(e.target.value))}
              />
            </div>

            <div className="form-field">
              <label className="field-label">Crop Harvest Quantity (kg)</label>
              <input
                type="number"
                step="50"
                className="input-text"
                value={quantityKg}
                onChange={(e) => setQuantityKg(Number(e.target.value))}
              />
            </div>

            <div className="form-field highlight-field">
              <label className="field-label">
                Transport Cost (INR) <span className="req-star">* Required</span>
              </label>
              <input
                type="number"
                placeholder="Leave blank to test safety block"
                className="input-text"
                value={transportCost}
                onChange={(e) => setTransportCost(e.target.value)}
              />
              <span className="field-help-text">
                Leave empty to verify that profit estimation is blocked when transport is unknown.
              </span>
            </div>

            <div className="form-field">
              <label className="field-label">Loading & Unloading (INR)</label>
              <input
                type="number"
                className="input-text"
                value={loadingCharges}
                onChange={(e) => setLoadingCharges(Number(e.target.value))}
              />
            </div>

            <div className="form-field">
              <label className="field-label">Market Cess / Commission (INR)</label>
              <input
                type="number"
                className="input-text"
                value={marketFees}
                onChange={(e) => setMarketFees(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="profit-action-row">
            <button
              className="btn-primary-large"
              onClick={handleCalculate}
              disabled={isCalculating}
            >
              Evaluate Net Proceeds
            </button>
          </div>

          {/* Results Breakdown */}
          {calcResult && (
            <div className={`profit-result-panel ${calcResult.is_calculable ? 'calculable' : 'blocked'}`}>
              {!calcResult.is_calculable ? (
                <div className="blocked-box">
                  <div className="blocked-header">
                    <AlertTriangle size={22} color="#c62828" />
                    <strong>Profit Calculation Blocked by Safety Policy</strong>
                  </div>
                  <p className="blocked-disclaimer">"{calcResult.disclaimer}"</p>
                  <p className="blocked-note">
                    {calcResult.safety_note}
                  </p>
                  <span className="tip-text">
                    Tip: Enter a transport estimate (e.g. ₹1500) above to calculate net proceeds.
                  </span>
                </div>
              ) : (
                <div className="calculated-box">
                  <div className="calc-header">
                    <CheckCircle size={22} color="#2e7d32" />
                    <strong>Net Proceeds Calculated with Complete Inputs</strong>
                  </div>

                  <div className="proceeds-summary-grid">
                    <div className="proceeds-col">
                      <span className="p-label">Gross Revenue</span>
                      <strong className="p-val">₹{calcResult.gross_revenue_inr?.toLocaleString()}</strong>
                      <span className="p-sub">({quantityKg} kg × ₹{sellingPrice}/kg)</span>
                    </div>

                    <div className="proceeds-col minus">
                      <span className="p-label">Total Expenses</span>
                      <strong className="p-val">- ₹{calcResult.total_estimated_costs_inr?.toLocaleString()}</strong>
                      <span className="p-sub">Transport + Labor + Fees</span>
                    </div>

                    <div className="proceeds-col net">
                      <span className="p-label">Estimated Net Proceeds</span>
                      <strong className="p-val highlight">
                        ₹{calcResult.estimated_net_proceeds_inr?.toLocaleString()}
                      </strong>
                      <span className="p-sub">Take-home return</span>
                    </div>
                  </div>

                  {calcResult.cost_breakdown && (
                    <div className="costs-table-mini">
                      <span>Expense Breakdown:</span>
                      <ul>
                        <li>Vehicle Transport: ₹{calcResult.cost_breakdown.transport_cost}</li>
                        <li>Loading / Unloading: ₹{calcResult.cost_breakdown.loading_charges}</li>
                        <li>Market Fees: ₹{calcResult.cost_breakdown.market_fees}</li>
                        <li>Packaging: ₹{calcResult.cost_breakdown.packaging_costs}</li>
                      </ul>
                    </div>
                  )}

                  <p className="disclaimer-footnote">
                    Disclaimer: {calcResult.disclaimer}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-done" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
