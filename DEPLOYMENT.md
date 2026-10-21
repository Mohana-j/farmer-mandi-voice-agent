# Production Deployment Guide: Vercel & Render

**Project:** Farmer Mandi Price Voice Agent  
**Event:** Agentic AI Hackathon 2026 — Powered by Ziro.Digital  
**Track:** Social Impact & Sustainability AI  

This document provides the exact, tested step-by-step instructions for deploying the **Farmer Mandi Price Voice Agent** with the **Frontend on Vercel** and the **Backend on Render**.

---

## 1. Identified Repository & Build Configuration

| Component | Setting | Value |
| :--- | :--- | :--- |
| **Frontend** | **Root Directory** | `frontend` |
| | **Framework Preset** | `Vite` |
| | **Build Command** | `npm run build` |
| | **Output Directory** | `dist` |
| | **Node.js Version** | `18.x` or `20.x` |
| | **Required Env Variable** | `VITE_API_URL` (Set to your Render backend URL) |
| **Backend** | **Root Directory** | Repository root (`.`) |
| | **Runtime** | `Python 3` (3.10 to 3.13) |
| | **Build Command** | `pip install -r backend/requirements.txt` |
| | **Start Command** | `python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| | **Health Check Path** | `/api/health` |
| | **Port Binding** | Reads `$PORT` dynamically from Render |

---

## 2. Order of Operations

Deploy in this order:
1. **Push your code to GitHub.**
2. **Deploy Backend to Render first** to obtain your public backend URL (`https://<service-name>.onrender.com`).
3. **Deploy Frontend to Vercel second**, passing the backend URL into `VITE_API_URL`.

---

## 3. Step-by-Step: Deploying Backend to Render

### Option A: Using the Render Blueprint (`render.yaml`) — Recommended
This repository includes a [`render.yaml`](./render.yaml) file at the root.

1. Log into your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ **Blueprint**.
3. Connect your GitHub repository.
4. Render will automatically detect [`render.yaml`](./render.yaml) and pre-fill all build commands, start commands, health checks, and environment variables.
5. Click **Apply**.
6. Wait for the build to complete (usually 1–2 minutes).
7. Copy your assigned service URL: `https://<your-backend-name>.onrender.com`.
8. Test the health endpoint: `https://<your-backend-name>.onrender.com/api/health`.

---

### Option B: Manual Web Service Setup on Render

1. Go to [Render Dashboard](https://dashboard.render.com) $\rightarrow$ **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name:** `farmer-mandi-agent-backend` (or your preferred name)
   - **Region:** Any (e.g., Oregon, Frankfurt)
   - **Branch:** `master` (or `main`)
   - **Root Directory:** *(leave blank — use repository root)*
   - **Runtime:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r backend/requirements.txt
     ```
   - **Start Command:**
     ```bash
     python -m uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free`
4. Expand **Advanced** and configure **Health Check Path**:
   - `/api/health`
5. Under **Environment Variables**, add:
   | Key | Value | Description |
   | :--- | :--- | :--- |
   | `PYTHONPATH` | `.` | Ensures root Python imports resolve cleanly |
   | `ENVIRONMENT` | `production` | Production mode |
   | `DATA_PROVIDER_MODE` | `synthetic` | Verified deterministic demo data mode (or `live`) |
   | `DATABASE_URL` | `sqlite:///./mandi_agent.db` | Local SQLite database (or PostgreSQL URL) |
   | `CORS_ORIGINS` | `*` | Allows calls from your Vercel frontend |
   | `EXPORT_DIRECTORY` | `./exports` | Export directory |
   | `GEMINI_API_KEY` | *(Optional)* | Only if you want live Gemini language parsing |
   | `LIVE_PORTAL_API_KEY` | *(Optional)* | Only if you have a registered `data.gov.in` key |
6. Click **Create Web Service**.
7. Once deployed, verify in your browser:
   - Health Check: `https://<your-backend-name>.onrender.com/api/health`
   - OpenAPI Docs: `https://<your-backend-name>.onrender.com/docs`

---

## 4. Step-by-Step: Deploying Frontend to Vercel

1. Log into your [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** $\rightarrow$ **Project**.
3. Import your GitHub repository.
4. In the **Configure Project** screen:
   - **Project Name:** `farmer-mandi-voice-agent`
   - **Framework Preset:** `Vite`
   - **Root Directory:** Click **Edit** and select **`frontend`**. *(Crucial step!)*
   - **Build and Output Settings:** Leave default (`npm run build`, `dist`).
5. Expand **Environment Variables** and add:
   | Key | Value |
   | :--- | :--- |
   | `VITE_API_URL` | `https://<your-backend-name>.onrender.com` |
   *(Ensure no trailing slash `/` at the end of the URL)*
6. Click **Deploy**.
7. Vercel will install dependencies, compile the TypeScript bundle, and publish your site in ~45 seconds.
8. Click the generated URL: `https://<your-project-name>.vercel.app`.

---

## 5. Post-Deployment Verification Checklist

Once both services are deployed, test your live production application:

- [ ] **Health Status Pill:** Check top-right of frontend dashboard. It should show `API Online` with a green dot.
- [ ] **Data Mode Badge:** Displays `Demo / Synthetic Mode` (amber) or `Live Portal Mode` (green).
- [ ] **Language Toggle:** Click between `English` and `தமிழ்` — all labels and buttons should instantly switch languages.
- [ ] **Voice / Text Query:**
  - Enter `Tomato`, `Grade A`, `Dharmapuri`, `50 km`.
  - Click **Search Verified Mandi Prices**.
  - Verified market cards, dated range, and Spoken Answer appear.
- [ ] **Voice Playback:** Click **Read Aloud** — SpeechSynthesis plays the grounded spoken answer.
- [ ] **Transport Safety Check:**
  - Click **Estimate Net Proceeds**.
  - Leaving transport blank displays: *"Transport cost is unknown. The most profitable market cannot be determined from price alone."*
  - Entering a transport cost displays net proceeds breakdown.
- [ ] **Human Approval Flow:**
  - Click **Export CSV** $\rightarrow$ Action Approval Modal pops up with Action ID and Idempotency Key.
  - Click **Approve & Execute Exactly Once**.
  - Green verification badge confirms export.
- [ ] **Official Test Suite:**
  - Navigate to **Test Suite** tab.
  - Click **Run All Tests**.
  - All four test cases (TC1, TC2, TC3, TC4) pass with green badges.

---

## 6. Database Persistence on Render

### SQLite Considerations (Free Tier)
- On Render's Free tier, the local filesystem is ephemeral and resets during service restarts.
- For a persistent SQLite database on Render:
  1. Upgrade to a paid instance ($7/month).
  2. Under **Disks**, add a persistent disk mounted at `/var/data` (e.g. 1 GB).
  3. Update `DATABASE_URL` to `sqlite:////var/data/mandi_agent.db`.

### PostgreSQL Database (Render Managed or Supabase)
- The backend fully supports PostgreSQL via SQLAlchemy and `psycopg2-binary`.
- If you spin up a free PostgreSQL database on Render or Supabase:
  1. Copy the internal or external database connection string.
  2. Set `DATABASE_URL=postgresql://user:password@hostname:5432/mandi_db`.
  3. The backend will automatically initialize tables on startup without requiring manual migrations.

---

## 7. Troubleshooting Common Deployment Issues

### CORS Blocked Errors
- **Symptom:** Browser console shows `CORS error: No 'Access-Control-Allow-Origin' header is present`.
- **Fix:** In your Render Web Service Environment Variables, ensure `CORS_ORIGINS` is set to `*` or includes your exact Vercel domain:
  `CORS_ORIGINS=https://farmer-mandi-voice-agent.vercel.app`

### Frontend 404 on API Calls
- **Symptom:** Calls to `/api/...` return 404 from Vercel.
- **Fix:** Ensure you added `VITE_API_URL` to your Vercel Environment Variables pointing to your Render service, and redeployed the frontend.

### Render Free Tier Cold Starts
- **Symptom:** First query takes 30–50 seconds to respond.
- **Explanation:** Free instances on Render spin down after 15 minutes of inactivity. Once woken by the first HTTP request, subsequent responses take under 100 ms.
