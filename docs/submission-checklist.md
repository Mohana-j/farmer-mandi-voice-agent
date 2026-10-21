# Official Hackathon Submission Checklist

**Hackathon:** Agentic AI Hackathon 2026 — Powered by Ziro.Digital  
**Project Name:** Farmer Mandi Price Voice Agent  
**Industry Category:** Social Impact & Sustainability AI  

---

## 1. Mandatory Functional Checklist

| Requirement | Implementation Status | Evidence / File Location |
| :--- | :---: | :--- |
| **Voice Query Support** | ✅ COMPLETED | Browser Web Speech STT in `frontend/src/services/speech.ts` with editable transcript fallback. |
| **Bilingual Interface (English & Tamil)** | ✅ COMPLETED | `frontend/src/i18n/translations.ts`, spoken voice synthesizer in English and Tamil. |
| **Crop, Grade, Location, Radius Inputs** | ✅ COMPLETED | `frontend/src/components/QueryForm.tsx`, `backend/app/schemas/schemas.py`. |
| **Unit Normalization (quintal/tonne to INR/kg)** | ✅ COMPLETED | `backend/app/services/normalizer.py`, tested in `test_normalization.py` and `TC3`. |
| **Date Freshness (today vs yesterday vs older)** | ✅ COMPLETED | `evaluate_data_freshness` in `normalizer.py`, tested in `TC2`. |
| **Source Provenance & Audit Trail** | ✅ COMPLETED | Retains source URL, record ID, retrieved_at, observation_date in DB `market_records`. |
| **Transport Cost Safety Rule** | ✅ COMPLETED | `backend/app/services/profitability.py`, verified in `TC4`. |
| **Action 1: Export Comparison (CSV)** | ✅ COMPLETED | `ExportService` in `export_service.py`, post-execution verification + SHA-256 hash. |
| **Action 2: Set Price Alert** | ✅ COMPLETED | `AlertService` in `alert_service.py`, simulated demo mode clearly labelled. |
| **Human-in-the-Loop Approval Gate** | ✅ COMPLETED | `backend/app/api/routes_actions.py`, modal in `ActionApprovalModal.tsx`. |
| **Idempotency Safeguard** | ✅ COMPLETED | Unique `idempotency_key` preventing duplicate exports/alerts on repeated clicks. |
| **Test Case TC1 (Tomato at 3 nearby mandis)** | ✅ COMPLETED | `OfficialTestCaseRunner.run_tc1()`, verified via Pytest and UI Test Dashboard. |
| **Test Case TC2 (Yesterday's data only)** | ✅ COMPLETED | `OfficialTestCaseRunner.run_tc2()`, verified via Pytest and UI Test Dashboard. |
| **Test Case TC3 (Quintal & kg price normalization)** | ✅ COMPLETED | `OfficialTestCaseRunner.run_tc3()`, verified via Pytest and UI Test Dashboard. |
| **Test Case TC4 (Transport cost unknown)** | ✅ COMPLETED | `OfficialTestCaseRunner.run_tc4()`, verified via Pytest and UI Test Dashboard. |
| **Public Mandi Portal Adapter** | ✅ COMPLETED | `MarketDataAdapter` in `market_adapter.py` (data.gov.in / Agmarknet schema). |
| **Synthetic Demo Data Provider** | ✅ COMPLETED | `DemoDataProvider` in `demo_data.py`, transparently tagged as `synthetic`. |
| **Automated Backend Pytest Suite** | ✅ COMPLETED | 23 automated tests passing in 0.18s (`backend/tests/`). |
| **Frontend Production Build** | ✅ COMPLETED | Vite React TypeScript builds cleanly in 1.79s (`frontend/dist/`). |
| **Dockerfile & docker-compose.yml** | ✅ COMPLETED | Unified multi-stage container build and compose setup. |
| **Architecture Documentation** | ✅ COMPLETED | `docs/architecture.md` with Mermaid workflow diagrams. |
| **Data Sources Document** | ✅ COMPLETED | `docs/data-sources.md` detailing API endpoints, limits & fallback. |
| **Official Test Report** | ✅ COMPLETED | `docs/test-report.md` with assertions and input fixtures. |
| **2-to-3 Minute Demo Video Script** | ✅ COMPLETED | `docs/demo-script.md` with second-by-second presenter cues. |
| **Deployment Guide** | ✅ COMPLETED | `docs/deployment.md` for Windows, macOS, Linux, and Cloud. |
| **Hackathon Presentation Deck** | ✅ COMPLETED | `docs/presentation.md` covering 12 required presentation topics. |

---

## 2. Participant Action Checklist (For Hackathon Submission)

*Note: The following items require external accounts and must be provided by the project owner upon submission:*

- [ ] **GitHub Repository:** Push this repository to your personal/team GitHub account.
- [ ] **Demo Video Recording:** Record a 2 to 3-minute video following `docs/demo-script.md` and upload to YouTube, Loom, or Google Drive.
- [ ] **Live Hosted Demo (Optional/Bonus):** Deploy the Docker container to Render, Railway, or Fly.io and supply the public URL.
- [ ] **Presentation Slides:** Export `docs/presentation.md` or present directly from Markdown/PowerPoint.
- [ ] **LinkedIn / Social Post:** Share your project post highlighting the social impact for Indian agriculture.
