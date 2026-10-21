# Official Test Report & Verification Audit

**Project:** Farmer Mandi Price Voice Agent  
**Hackathon:** Agentic AI Hackathon 2026 — Powered by Ziro.Digital  
**Test Suite Status:** 100% Passing (23/23 Pytest Unit & Integration Tests, 4/4 Official Test Cases)  
**Execution Date:** 2026-10-21  

---

## 1. Executive Test Summary

| Test Suite | Total Tests | Passed | Failed | Status | Duration |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Official Hackathon Test Cases (TC1–TC4)** | 4 | 4 | 0 | **PASSED** | 2.18 ms |
| **Price Normalization & Units** | 7 | 7 | 0 | **PASSED** | 0.04 s |
| **Data Freshness Engine** | 4 | 4 | 0 | **PASSED** | 0.02 s |
| **Profitability Safety Engine** | 2 | 2 | 0 | **PASSED** | 0.01 s |
| **Human-in-the-Loop Approval & Idempotency** | 2 | 2 | 0 | **PASSED** | 0.05 s |
| **End-to-End FastAPI Routes** | 4 | 4 | 0 | **PASSED** | 0.06 s |
| **Total Automated Suite** | **23** | **23** | **0** | **100% PASS** | **0.18 s** |

---

## 2. Four Mandatory Official Test Cases

### TC1 — Tomato at Three Nearby Markets

- **Objective:** Verify price normalization to INR/kg, dated price range computation across three eligible nearby markets, grounded voice answer generation, and absence of unsupported live-data claims.
- **Input Fixture:**
  - Crop: `Tomato`, Grade: `Grade A`, Location: `Dharmapuri`, Radius: `50.0 km`
  - Records:
    1. Dharmapuri Regulated Market: ₹2,000 / quintal
    2. Palacode APMC: ₹2,200 / quintal
    3. Pennagaram Uzhavar Sandhai: ₹24.00 / kg
- **Expected Result:**
  - Exactly 3 eligible records compared.
  - Normalized prices: ₹20.00/kg, ₹22.00/kg, ₹24.00/kg.
  - Dated price range: `₹20.00 to ₹24.00 per kg`.
  - Spoken response quotes actual observation dates.
  - Transparent `[Demo Mode]` tag (no fabricated live claim).
- **Actual Result:**
  - Usable count: `3`
  - Normalized range: `₹20.00 to ₹24.00 per kg`
  - Voice Answer: `[Demo Mode] I found verified records for 3 nearby markets. The recorded tomato prices range from ₹20.00 to ₹24.00 per kilogram...`
- **Assertions Passed:**
  - `[PASS]` Exactly three nearby market records were processed.
  - `[PASS]` Dated price range correctly calculated as ₹20.00 to ₹24.00 per kg.
  - `[PASS]` Observation date correctly captured in summary.
  - `[PASS]` Voice answer reports normalized price bounds accurately.
  - `[PASS]` Demo mode transparently communicated without false live-data claims.
- **Status:** **PASSED**

---

### TC2 — Only Yesterday's Data Available

- **Objective:** Verify data freshness classifier identifies past-day data, agent explicitly speaks "Yesterday's data", quotes the observation date, and never claims yesterday's price is today's price.
- **Input Fixture:**
  - Crop: `Tomato`, Grade: `Grade A`, Location: `Dharmapuri`
  - Records: Only yesterday's dated fixtures (e.g., `2026-10-20`).
- **Expected Result:**
  - Freshness category: `yesterday`.
  - Spoken response explicitly declares "Yesterday's data".
  - Observation date read aloud.
  - No claim that yesterday's price represents current trading.
- **Actual Result:**
  - Freshness category: `yesterday`
  - Voice Answer: `[Demo Mode] ... Notice: Only yesterday's data is available, dated 2026-10-20. Today's trading prices may differ...`
- **Assertions Passed:**
  - `[PASS]` All retrieved records correctly classified as yesterday's data.
  - `[PASS]` Voice answer explicitly declares 'Only yesterday's data is available'.
  - `[PASS]` Spoken response clearly quotes actual observation date (2026-10-20).
  - `[PASS]` Agent strictly avoids claiming yesterday's price is today's price.
- **Status:** **PASSED**

---

### TC3 — Quintal and Kilogram Prices Normalization

- **Objective:** Verify deterministic unit conversions (1 quintal = 100 kg, 1 tonne = 1,000 kg) and ensure unsupported units are rejected without guessing.
- **Input Fixture:**
  - Case A: ₹2,400.00 / quintal
  - Case B: ₹24.00 / kg
  - Case C: ₹24,000.00 / tonne
  - Case D: ₹1,500.00 / unknown_bag
- **Expected Result:**
  - Cases A, B, C normalize identically to ₹24.00 / kg.
  - Case D is rejected with `unknown_unit` error.
- **Actual Output:**
  - 2,400 INR/quintal $\div 100 = 24.00\text{ INR/kg}$
  - 24.00 INR/kg $\div 1 = 24.00\text{ INR/kg}$
  - 24,000 INR/tonne $\div 1,000 = 24.00\text{ INR/kg}$
  - 1,500 INR/unknown_bag $\rightarrow$ `None` (Unsupported unit)
- **Assertions Passed:**
  - `[PASS]` 2400.0 INR/quintal correctly normalized to ₹24.00/kg.
  - `[PASS]` 24.0 INR/kg correctly normalized to ₹24.00/kg.
  - `[PASS]` 24000.0 INR/tonne correctly normalized to ₹24.00/kg.
  - `[PASS]` Invalid unit 'INR/unknown_bag' safely rejected without guessing conversion.
- **Status:** **PASSED**

---

### TC4 — Transport Cost Unknown Safety Enforcement

- **Objective:** Verify agent refuses to declare the highest-price market "the best profit" when transport costs are omitted, and outputs the exact required safety disclaimer.
- **Input Fixture:**
  - Scenario 1 (Missing transport): Price = ₹28.00/kg, Quantity = 1,000 kg, Transport = `None`.
  - Scenario 2 (Complete inputs): Price = ₹28.00/kg, Quantity = 1,000 kg, Transport = ₹2,500, Fees = ₹900.
- **Expected Result:**
  - Scenario 1: `is_calculable = False`, disclaimer = `"Transport cost is unknown. The most profitable market cannot be determined from price alone."`
  - Scenario 2: Gross = ₹28,000, Costs = ₹3,400, Net Proceeds = ₹24,600.
- **Actual Output:**
  - Scenario 1 calculable: `False`
  - Scenario 1 disclaimer: `"Transport cost is unknown. The most profitable market cannot be determined from price alone."`
  - Scenario 2 Net Proceeds: `₹24,600.00`
- **Assertions Passed:**
  - `[PASS]` Profitability engine strictly returned is_calculable=False when transport cost is absent.
  - `[PASS]` Exact mandatory disclaimer returned: 'Transport cost is unknown. The most profitable market cannot be determined from price alone.'
  - `[PASS]` Proceeds and revenue fields remain safely null when inputs are incomplete.
  - `[PASS]` When transport cost (₹2500) and fees are supplied, net proceeds are calculated accurately (₹24,600).
- **Status:** **PASSED**

---

## 3. Human Approval Gate & Idempotency Audit

- Tested with `backend/tests/test_actions_approval.py` and `test_api.py`.
- **Pre-execution preview:** Action record stored in database with `approval_status="pending"`.
- **First approval:** Validates matching `idempotency_key`, writes CSV / registers alert, performs post-execution filesystem & SHA-256 integrity verification.
- **Repeated approval:** Replay attack / duplicate click detected; server returns existing verified record with message `Action was previously executed and verified (Idempotent response).` No duplicate records or files created.
- **Rejection test:** Unapproved action marked `rejected` and left completely unexecuted on filesystem and database.
