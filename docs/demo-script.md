# Hackathon Video Demo Script (2 to 3 Minutes)

**Project Name:** Farmer Mandi Price Voice Agent  
**Event:** Agentic AI Hackathon 2026 — Powered by Ziro.Digital  
**Target Duration:** 2 minutes 30 seconds  

---

## Demo Script Timeline & Narration

### [0:00 – 0:20] Problem & Social Impact (20 seconds)
- **Visual:** Show dashboard with green agricultural accents and bilingual toggle (English / தமிழ்).
- **Narration:**
  > *"Across India, smallholder farmers lose up to 25% of their potential income simply because they lack timely, transparent access to nearby mandi prices. When a farmer asks: 'What is today's tomato price nearby?', typical chatbots hallucinate numbers or confuse quintal prices with kilogram prices. Today, we present the Farmer Mandi Price Voice Agent — an agentic AI system with verified provenance, deterministic unit conversion, and strict economic safety guardrails."*

---

### [0:20 – 0:45] Asking the Voice Query (25 seconds)
- **Visual:** Click on the 'Farmer Query' tab. Click 'Start Speaking' (Microphone button) or demonstrate with Tamil voice toggle.
- **Action:** Speak into microphone: *"What is today's tomato price in Dharmapuri?"*
- **Visual:** The live speech transcript appears in the editable box. Show that the farmer can review or edit the text before clicking search.
- **Narration:**
  > *"Our agent supports natural voice input in English and Tamil. Farmers see an editable transcript, ensuring full user agency before any search is triggered. Let's submit the query."*

---

### [0:45 – 1:15] Grounded Market Comparison & Spoken Answer (30 seconds)
- **Visual:** Results screen loads with the Spoken Answer Card and Market Comparison Grid. Click 'Read Aloud' (English or Tamil).
- **Voice Agent Audio plays:**
  > *"[Demo Mode] I found verified records for 3 nearby markets. The recorded tomato prices range from ₹21.00 to ₹24.00 per kilogram. These records are dated today. Source: synthetic-fixture-tn. Transport cost is unknown; the highest price market is not guaranteed to be the most profitable."*
- **Visual:** Point to the comparison table showing original reported prices (₹2,200/quintal) beside normalized prices (₹22.00/kg).
- **Narration:**
  > *"Notice how the agent operates: all units are deterministically converted to INR per kilogram. The audio explicitly quotes observation dates, data source provenance, and reminds the farmer that market price alone is not a guarantee of profit."*

---

### [1:15 – 1:40] Profitability Safety & Yesterday's Data Handling (25 seconds)
- **Visual:** Point to the red safety banner: *"Transport cost is unknown. The most profitable market cannot be determined from price alone."*
- **Action:** Click 'Estimate Net Proceeds'.
  - Leave transport cost empty $\rightarrow$ Show the safety block: Profit calculation is strictly blocked.
  - Enter transport cost: ₹2,000 $\rightarrow$ Instantly displays Gross Revenue, Cost Breakdown, and true Net Proceeds.
- **Narration:**
  > *"A critical safety feature of our agent: it never declares a distant high-price market 'the most profitable'. Distance and vehicle hire can turn an apparent ₹2 premium into a severe net loss. Profitability estimation is safely blocked until real transport costs are supplied."*

---

### [1:40 – 2:05] Human-in-the-Loop Action Approval & Verification (25 seconds)
- **Visual:** Click 'Export CSV'. An Action Approval Modal appears with Action ID, Idempotency Key, Destination, and Preview Data.
- **Action:** Click 'Approve & Execute Exactly Once'.
- **Visual:** Show post-execution verification: green verification badge, row count check, and SHA-256 hash.
- **Narration:**
  > *"Our agent implements a strict Human-in-the-Loop approval gate for critical actions like exports and price alerts. No action executes without explicit approval, each run is guarded by an idempotency key to prevent double execution, and the resulting file is verified on disk with SHA-256 integrity."*

---

### [2:05 – 2:30] Evidence & Audit Trail + 4 Passing Official Tests (25 seconds)
- **Visual:** Switch to 'Evidence & Audit' tab to show the tool timeline, state transitions, and normalization decisions.
- **Visual:** Switch to 'Test Suite' tab and click 'Run All Tests'. Show TC1, TC2, TC3, and TC4 running and displaying green 'PASSED' badges in real time.
- **Narration:**
  > *"Finally, every decision is auditable. Our official test dashboard verifies all four mandatory hackathon test cases: three nearby markets, yesterday-only freshness, quintal-to-kilogram conversion, and transport cost safety. With 23 automated tests passing, the Farmer Mandi Price Voice Agent is production-ready, trustworthy, and built for real social impact."*
