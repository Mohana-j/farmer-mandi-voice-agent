# Deployment & Local Operations Guide

**Project:** Farmer Mandi Price Voice Agent  
**Event:** Agentic AI Hackathon 2026 — Powered by Ziro.Digital  

---

## 1. System Requirements

- **Python:** 3.10 to 3.13
- **Node.js:** v18.0.0 or higher (v20+ recommended, v22 tested)
- **Package Managers:** pip and npm
- **Operating Systems:** Windows 10/11, macOS, Ubuntu/Debian Linux

---

## 2. Local Development Setup

### A. Clone & Prepare Directory
```bash
cd ziro
```

### B. Backend Setup
```bash
# 1. Create Python virtual environment
python -m venv backend/.venv

# 2. Activate virtual environment
# Windows (PowerShell):
backend\.venv\Scripts\Activate.ps1
# Linux / macOS:
source backend/.venv/bin/activate

# 3. Install backend dependencies
pip install -r backend/requirements.txt

# 4. Configure environment variables
cp .env.example .env
```

### C. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## 3. Running the Application Locally

### Starting Backend (FastAPI on Port 8000)
```powershell
# Windows PowerShell:
$env:PYTHONPATH="."
backend\.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
```bash
# Linux / macOS:
PYTHONPATH=. backend/.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- API Health Status: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Starting Frontend (Vite on Port 5173)
```bash
cd frontend
npm run dev
```
- Open your browser to: [http://localhost:5173](http://localhost:5173)

---

## 4. Running the Automated Test Suite

### Backend Pytest Suite (All 23 Tests)
```powershell
$env:PYTHONPATH="."
backend\.venv\Scripts\python -m pytest backend/tests -v
```

### Frontend Production Build Test
```bash
cd frontend
npm run build
```

---

## 5. Docker & Container Deployment

### Running with Docker Compose
```bash
# Build and run the unified container
docker-compose up --build -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```
Access the application at [http://localhost:8000](http://localhost:8000).

### Manual Docker Build
```bash
docker build -t farmer-mandi-voice-agent:latest .
docker run -p 8000:8000 -v mandi-exports:/app/exports farmer-mandi-voice-agent:latest
```

---

## 6. Cloud Deployment Targets

### Option 1: Render / Railway / Fly.io (PaaS)
1. Link your Git repository.
2. Set build command:
   ```bash
   pip install -r backend/requirements.txt && cd frontend && npm install && npm run build && cd ..
   ```
3. Set start command:
   ```bash
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Attach a persistent disk volume to `/app/exports` and `/app/data` to retain SQLite databases and CSV export files.
5. Provide environment variables from `.env.example`.

### Option 2: Production Database Upgrade (PostgreSQL)
To scale beyond local SQLite:
1. Provision a managed PostgreSQL instance (e.g. Supabase, Neon, AWS RDS).
2. Install `psycopg2-binary` or `asyncpg`.
3. Set `DATABASE_URL=postgresql://user:pass@host:5432/mandi_db`.
4. SQLAlchemy models will initialize tables automatically on startup.
