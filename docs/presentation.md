# Hackathon Pitch & Presentation Deck

**Project:** Farmer Mandi Price Voice Agent  
**Category:** Social Impact & Sustainability AI  
**Event:** Agentic AI Hackathon 2026 — Powered by Ziro.Digital  
**Team:** AI Architects, Full-Stack Engineers & Domain Specialists  

---

## Slide 1: Title & Vision

# Farmer Mandi Price Voice Agent
### Empowering Smallholder Farmers with Grounded AI, Verified Mandi Prices & Economic Safety

- **Category:** Social Impact & Sustainability AI
- **Tagline:** Transparent, dated agricultural market prices in English and Tamil — with zero hallucination.
- **Powered by:** Ziro.Digital Agentic AI Framework

---

## Slide 2: The Problem & Real-World Pain Points

### Why Indian Farmers Lose Income
1. **Linguistic & Literacy Barriers:** 68% of smallholder farmers struggle with dense tabular government portals on mobile phones.
2. **Unit Confusion:** Mandis quote in quintals (₹2,200/q), tonnes, or regional crates, while retail and farmgate calculations happen in kilograms.
3. **Date Ambiguity:** Farmers often travel to distant markets based on yesterday's or last week's peak prices, arriving to market gluts.
4. **Transport Cost Blindspots:** Naive advice tells farmers to sell at the highest nominal price, ignoring vehicle hire that turns profits into losses.
5. **Hallucination Risk in Generic LLMs:** Standard chatbots cheerfully invent market prices when asked, creating catastrophic financial risk.

---

## Slide 3: The Proposed Solution

### An Agentic AI Partner Built for the Field
- **Natural Voice Interaction:** Speak in English or Tamil; review editable transcripts before running searches.
- **Deterministic Arithmetic:** Exact conversion from quintals/tonnes to INR/kg.
- **Provenance & Freshness Traceability:** Transparent distinction between today's live trading and yesterday's records.
- **Profitability Safety Rule:** Never claims a market is "most profitable" when transport cost is unknown.
- **Human-in-the-Loop Approval:** Exports and price alerts require explicit farmer authorization before execution.

---

## Slide 4: Agentic AI Workflow & Tool Pipeline

```mermaid
flowchart LR
    A[Voice / Text Query] --> B[parse_query Tool]
    B --> C[validate_query Tool]
    C --> D[discover_sources Tool]
    D --> E[fetch_records Tool]
    E --> F[normalize_units Tool]
    F --> G[assess_grade Tool]
    G --> H[evaluate_freshness Tool]
    H --> I[compare_markets Tool]
    I --> J[generate_voice_response Tool]
    J --> K[Approval Gate]
```

- Discrete tool boundaries and explicit state persistence in SQLite.
- Auditable JSON event logs for every tool invocation.

---

## Slide 5: The LLM vs. Deterministic Boundary

### Responsible AI Design
- **Google Gemini API Adapter:** Utilized strictly for natural language query parsing and multilingual translation.
- **Transparent Deterministic Fallback:** Operates 100% offline without API keys; never pretends a fallback was a live LLM call.
- **Hard Business Rules in Python:** All price math, unit conversions, freshness checks, and profit calculations run through deterministic code.
- **Zero Hallucination Guarantee:** If data does not exist, the agent discloses the absence rather than guessing.

---

## Slide 6: Profitability Safety & Economic Realism

### Enforcing Responsible Advice
When transport costs are missing:
> **"Transport cost is unknown. The most profitable market cannot be determined from price alone."**

When farmer supplies real expenses:
$$\text{Net Proceeds} = (\text{Quantity} \times \text{Price}) - (\text{Transport} + \text{Loading} + \text{Mandi Fees})$$

- Prevents farmers from driving 50 km for a ₹2/kg price gain that costs ₹3,000 in truck hire.

---

## Slide 7: Human-in-the-Loop Actions & Idempotency

### Action Safeguards
1. **Export Market Comparison (CSV):**
   - Action preview shows filename, destination, rows, and fields.
   - Requires explicit approval click.
   - Independent post-execution verification: checks file on disk, validates line counts, and generates SHA-256 hash.
2. **Price Alerts:**
   - Previews threshold condition and market target.
   - Idempotency key prevents duplicate execution on repeated clicks or network retries.
   - Tagged as simulated notification in demo mode.

---

## Slide 8: Official Test Suite Results (TC1 – TC4)

### 100% Passing Verification

| Test Case | Scenario Tested | Outcome | Assertion Result |
| :--- | :--- | :---: | :---: |
| **TC1** | Tomato at 3 nearby mandis | **PASSED** | Normalized ₹20–₹24/kg, dates & source traceable |
| **TC2** | Only yesterday's data available | **PASSED** | Explicitly speaks "Yesterday's data", observation date quoted |
| **TC3** | Quintal & Kilogram price mix | **PASSED** | 2400/quintal = ₹24/kg, invalid units rejected |
| **TC4** | Transport cost unknown | **PASSED** | Blocked without transport cost; calculates net with inputs |

*Plus 19 additional automated unit tests covering API routes, freshness, and approval guards.*

---

## Slide 9: User Experience & Bilingual Accessibility

- **Modern Farmer-Centric UI:** Green agricultural color scheme, accessible high-contrast text, large touch targets.
- **English and Tamil:** Full UI bilingual toggle and speech synthesis for both languages.
- **Editable Transcript:** Farmers can inspect or correct voice recognition errors before running queries.
- **Offline / Mobile Friendly:** Responsive on smartphones, tablets, and desktop displays.

---

## Slide 10: Deployment & Scalability

- **Unified Docker Architecture:** Multi-stage build with FastAPI backend and Vite React frontend.
- **Persistent Storage:** SQLite for local demonstrations; easily scales to PostgreSQL on AWS RDS or Supabase.
- **Permitted Data Adapters:** Open Government Data Platform (data.gov.in) with graceful fallback to deterministic fixtures.

---

## Slide 11: Limitations & Future Roadmap

### Current Limitations (Disclosed Honestly)
- Real-time GPS distance calculation requires phone geolocation permission (defaults to reference town distance).
- Live portal access depends on government server availability during morning trading hours.

### Future Improvements
1. **Direct IVR / Phone Call Integration:** Connect to toll-free farmer helplines via Twilio or Asterisk.
2. **WhatsApp / SMS Gateway:** Real-time push alerts via official farmer cooperative integrations.
3. **Hyperlocal Crowd-Sourced Price Reporting:** Peer-verified arrival records from farmer producer organizations (FPOs).

---

## Slide 12: Conclusion

### Technology in Service of Farmers
The **Farmer Mandi Price Voice Agent** proves that agentic AI can be transparent, economically grounded, and genuinely useful.

- **Trustworthy:** Every price traced to observation dates and source IDs.
- **Safe:** Blocks premature profit claims and protects farmer capital.
- **Accessible:** Voice-first in local languages for smallholders across India.
