# Contributing to CiteVerify AI

Welcome to **CiteVerify AI** for INNOVEDGE 2026 Hackathon (Problem Statement 03).
Please follow these guidelines to keep our 4-agent parallel monorepo coordinated and stable.

---

## 1. Team Monorepo Structure & Ownership

| Developer / Agent | Role | Directory Ownership | Working Branch |
|---|---|---|---|
| **Agent 1** | Frontend Architect | `frontend/**` | `feature/frontend` |
| **Agent 2** | Backend Architect | `backend/**`, `scripts/**` | `feature/backend` |
| **Agent 3** | AI/ML Engineer | `ai_engine/**` | `feature/ai-engine` |
| **Agent 4** | Research Integration | `research_services/**`, `tests/integration/**` | `feature/research-api` |

---

## 2. Setting Up Your Development Environment

### 2.1. Backend Setup
```bash
# In Git Bash:
python -m venv backend/.venv
source backend/.venv/Scripts/activate
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt

# In PowerShell:
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r backend\requirements-dev.txt
```

### 2.2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 3. Development Workflow

1. **Keep Your Branch Updated:**
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/your-role
   git rebase main
   ```
2. **Commit Style:** Use Conventional Commits (`feat(...)`, `fix(...)`, `test(...)`, `docs(...)`).
3. **Run Checks Before Opening a PR:**
   ```bash
   python scripts/validate_repo.py
   pytest backend/tests -v
   npm --prefix frontend run build
   ```
4. **Contract Changes:** If you need a field added or modified in API responses, DO NOT edit implementation files directly. Open a `contract-change` issue first.

---

## 4. Honesty Rule
Never fabricate citations, DOIs, papers, passages, or test results. Insufficient evidence must result in `verdict = null` and `verification_state = UNABLE_TO_VERIFY` or `REQUIRES_HUMAN_REVIEW`.
Every evidence passage must explicitly set `evidence_level` (`FULL_TEXT`, `ABSTRACT_ONLY`, `METADATA_ONLY`, `NONE`).

