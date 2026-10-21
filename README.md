# Farmer Mandi Price Voice Agent 🌾

> **Empowering smallholder farmers with verified agricultural mandi prices, deterministic unit normalizations, bilingual voice assistance (English & Tamil), and strict economic safety guardrails.**

🏆 **Official Submission for the Agentic AI Hackathon 2026 — Powered by Ziro.Digital**  
**Track:** Social Impact & Sustainability AI  
**Status:** 100% Hackathon-Ready, Fully Tested & Deployable  

---

## 🌟 Overview & Problem Statement

Across rural India, smallholder farmers often ask:
> *"What is today's tomato price at nearby markets?"*

Traditional search engines and generic AI chatbots routinely fail Indian agriculture:
1. They hallucinate prices or confuse regional trading units (₹2,200 per quintal reported as ₹2,200 per kilogram).
2. They fail to disclose whether prices represent today's morning trading or yesterday's stale records.
3. They irresponsibly declare a distant market "the most profitable" purely based on nominal price, ignoring truck hire that turns an apparent ₹2/kg premium into a crippling net loss.

The **Farmer Mandi Price Voice Agent** solves this through a grounded multi-step agentic architecture:
- 🗣️ **Voice-First in English and Tamil:** Farmers speak naturally; browser SpeechRecognition provides an editable transcript before running searches.
- ⚖️ **Deterministic Unit Normalization:** Converts quintals (100 kg) and metric tonnes (1,000 kg) to INR/kg in tested Python arithmetic — never guessing or approximating.
- 📅 **Strict Provenance & Freshness Engine:** Explicitly distinguishes today's trading from yesterday's data, quoting the exact observation date and source portal record ID.
- 🛡️ **Mandatory Transport Safety Rule:** Strictly enforces the policy: *"Transport cost is unknown. The most profitable market cannot be determined from price alone."* Calculation is blocked until real costs are supplied.
- 🤝 **Human-in-the-Loop Action Gate:** Exporting market comparisons (CSV) and setting price alerts require explicit human approval, protected by unique idempotency keys and post-execution SHA-256 verification.
- 🧪 **Four Mandatory Hackathon Test Cases (TC1–TC4):** Fully automated with live assertions in the UI Test Dashboard and Pytest.

---

## 🛠️ Technology Stack

| Layer | Technologies Used | Justification |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, TypeScript, Lucide Icons, Plain CSS | Fast, accessible, mobile-first responsive design with green agricultural accents and high contrast. |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy | High-performance asynchronous REST API with OpenAPI/Swagger documentation and strict schema validation. |
| **Database** | SQLite (with PostgreSQL compatibility) | Zero-configuration local demonstration with persistent storage for queries, records, alerts, and audit logs. |
| **AI & Orchestration**| Multi-step State Machine + Google Gemini Adapter | Segregates linguistic parsing from deterministic business rules. 100% functional in offline fallback mode without paid API keys. |
| **Voice / Speech** | Browser Web Speech API (STT & TTS) | Client-side SpeechRecognition with editable transcript and SpeechSynthesis in English and Tamil (`ta-IN`). |
| **Testing** | Pytest, AsyncIO | 23 automated tests covering TC1–TC4, conversions, freshness, approval gates, and idempotency. |
| **Deployment** | Docker, Docker Compose, PowerShell scripts | Containerized multi-stage production deployment ready for Render, Railway, or local servers. |

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- Python 3.10 to 3.13
- Node.js v18+ (Node v20 or v22 recommended)
- Git

### 1. Clone the Repository
```bash
git clone <your-repo-url> ziro
cd ziro
```

### 2. Backend Setup
```bash
# Create Python virtual environment
python -m venv backend/.venv

# Activate environment (Windows PowerShell)
backend\.venv\Scripts\Activate.ps1
# Or Linux / macOS:
# source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment variables
cp .env.example .env
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 4. Run Development Servers

**Option A — Automated Script (Windows PowerShell):**
```powershell
.\scripts\run_dev.ps1
```

**Option B — Manual Terminal Startup:**
- **Terminal 1 (Backend API):**
  ```powershell
  $env:PYTHONPATH="."
  backend\.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Terminal 2 (Frontend Client):**
  ```bash
  cd frontend
  npm run dev
  ```

Open your browser to:
- **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 🧪 Running Automated Tests

Run the complete 23-test Pytest suite:
```powershell
$env:PYTHONPATH="."
backend\.venv\Scripts\python -m pytest backend/tests -v
```

### The 4 Mandatory Official Test Cases
Navigate to the **Test Suite** tab in the web UI or run via API:

1. **TC1 — Tomato at Three Nearby Markets:** Verifies normalization across 3 nearby mandis to INR/kg, dated price range computation, and grounded spoken answer.
2. **TC2 — Only Yesterday's Data Available:** Verifies that stale data is classified as "yesterday", quotes the observation date aloud, and avoids claiming yesterday's price represents today's trading.
3. **TC3 — Quintal and Kilogram Prices:** Verifies that ₹2,400/quintal is converted to ₹24.00/kg, ₹24,000/tonne is converted to ₹24.00/kg, and unknown units are rejected.
4. **TC4 — Transport Cost Unknown:** Confirms that the agent refuses to declare "best profit" without transport costs, outputting the exact required safety disclaimer.

---

## 🐳 Docker Deployment

Run the complete containerized stack using Docker Compose:
```bash
docker-compose up --build -d
```
Access the application at [http://localhost:8000](http://localhost:8000).

---

## 📁 Repository Directory Structure

```
ziro/
├── backend/
│   ├── app/
│   │   ├── agents/            # Multi-step state machine orchestrator & explicit tools
│   │   ├── api/               # FastAPI route modules (queries, actions, alerts, tests)
│   │   ├── config.py          # Settings and environment validation
│   │   ├── database.py        # SQLAlchemy database engine and session
│   │   ├── models/            # Database schema models (FarmerQuery, MarketRecord, etc.)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   └── services/          # Core engines (normalizer, safety, demo_data, market_adapter)
│   ├── tests/                 # 23 automated Pytest test cases
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # UI components (Header, Dashboard, Comparison, Modals, Tests)
│   │   ├── i18n/              # English & Tamil translations
│   │   ├── services/          # API client and Web Speech STT/TTS adapters
│   │   ├── types/             # TypeScript interfaces
│   │   ├── App.tsx            # Root application view
│   │   └── App.css            # High-contrast, responsive farmer styling
│   ├── package.json           # Frontend dependencies
│   └── vite.config.ts         # Vite bundler configuration
├── docs/
│   ├── architecture.md        # Technical architecture, state machine & Mermaid diagrams
│   ├── data-sources.md        # Market data integration & access guidelines
│   ├── test-report.md         # Full test audit and TC1-TC4 assertions
│   ├── demo-script.md         # 2.5 minute video demo presenter script
│   ├── deployment.md          # Production cloud & container deployment instructions
│   ├── presentation.md        # Hackathon pitch deck slides
│   └── submission-checklist.md# Mandatory hackathon requirements verification
├── scripts/                   # PowerShell helper scripts (run_dev, run_tests, build_all)
├── .env.example               # Environment variables template
├── .gitignore                 # Secret and artifact exclusion rules
├── Dockerfile                 # Unified multi-stage production container
├── docker-compose.yml         # Container orchestration configuration
└── README.md                  # Main documentation
```

---

## 🛡️ Responsible AI & Ethical Guidelines

- **No Hallucinated Market Data:** When real records are unavailable, the agent admits the absence rather than inventing prices.
- **Transparent Demo Mode:** Synthetic records are clearly watermarked as `[Demo Mode]` and `synthetic` across the audio, UI badges, and database.
- **Farmer Capital Protection:** We treat transport costs and market fees as essential economic variables, preventing harmful speculative trips to distant mandis.
- **Privacy First:** Voice recordings are processed in the browser; no personal audio is transmitted or sold to third parties.

---

## 📜 License
This project is open-source under the MIT License for the **Agentic AI Hackathon 2026 — Powered by Ziro.Digital**.
