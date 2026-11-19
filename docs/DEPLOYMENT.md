# Production Deployment Guide (Free Tier / ₹0 Budget)

This guide documents deploying CiteVerify AI to free cloud hosting providers without incurring infrastructure costs.

---

## 1. Hosting Architecture Overview

| Component | Target Platform | Free Tier Specifications | Start Command / Root Dir |
|---|---|---|---|
| **Frontend** | Vercel | Free Hobby Plan | Root Directory: `frontend/`<br>Build: `npm run build` |
| **Backend** | Render / Railway / Fly.io | Free Web Service Tier | Root Directory: `.`<br>Start: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT` |
| **Database (Optional)** | Supabase | Free Shared PostgreSQL | 500MB database, 2 projects free |

---

## 2. Environment Variables & Cross-Service Configuration

```
[ Frontend on Vercel ]
   │
   │ NEXT_PUBLIC_API_BASE_URL = https://citeverify-backend.onrender.com
   │
   ▼
[ Backend on Render ]
   ├── CORS_ORIGINS = https://citeverify.vercel.app,http://localhost:3000
   ├── LLM_API_KEY = (Google AI Studio Gemini Free Key)
   ├── OPENALEX_EMAIL = researcher@example.com
   └── DATABASE_URL = (Optional Supabase Postgres Connection String)
```

> [!WARNING]
> **Ephemeral Disk Warning:** Free tiers on Render, Railway, and Fly use ephemeral filesystems. Files saved to `uploads/` will be wiped when the container sleeps or restarts. Uploaded PDFs are processed in-flight during the verification pipeline; all permanent claims and reports must be stored in the database.

> [!NOTE]
> **Cold Start Mitigation:** Free tier instances sleep after 15 minutes of inactivity. First requests can take 30–50 seconds to boot. The frontend UI displays a polite "Waking backend service..." status badge until `/api/health` responds.

---

## 3. Frontend Deployment (Vercel)

1. Connect the GitHub repository in the Vercel dashboard.
2. Set **Root Directory** to `frontend`.
3. Set **Framework Preset** to Next.js.
4. Add Environment Variables:
   - `NEXT_PUBLIC_API_BASE_URL`: The production URL of the backend service.
   - `NEXT_PUBLIC_USE_MOCKS`: `false` (CRITICAL for production).
5. Click **Deploy**.

---

## 4. Backend Deployment (Render / Railway)

1. Connect repository in Render Dashboard -> **New Web Service**.
2. Settings:
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`
3. Add Environment Variables:
   - `CORS_ORIGINS`: Comma-separated Vercel URLs (e.g. `https://citeverify.vercel.app`).
   - `LLM_PROVIDER`: `gemini`
   - `LLM_API_KEY`: Secret API key.
   - `OPENALEX_EMAIL`: Team contact email.
   - `CROSSREF_EMAIL`: Team contact email.
4. Verify deployment by visiting `https://<your-service>.onrender.com/api/health`.

---

## 5. Deployment Verification Checklist
- [ ] Backend `/api/health` returns `200 OK` with JSON envelope.
- [ ] Frontend loads without console errors.
- [ ] Vercel client successfully makes cross-origin requests to backend (CORS verified).
- [ ] `NEXT_PUBLIC_USE_MOCKS` is strictly `false` on production domains.
- [ ] No API keys or service role secrets exposed in client network inspection.

