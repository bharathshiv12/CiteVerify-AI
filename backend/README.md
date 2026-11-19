# CiteVerify AI - Backend Service

FastAPI-powered backend handling PDF document staging, pipeline orchestration, database persistence, and REST endpoints for CiteVerify AI.

---

## 1. Quick Start

### Create & Activate Virtual Environment
```bash
# Git Bash
python -m venv .venv
source .venv/Scripts/activate

# PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Configure Environment
```bash
cp .env.example .env
```

### Run Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive API documentation: `http://localhost:8000/api/docs`.

---

## 2. Testing
```bash
pytest -v
```

---

## 3. Architecture & Ownership
- **Owner**: Agent 2 (Backend Developer)
- **Shared Schemas**: `app/schemas/` derived directly from `contracts/schemas/`.
- **Database**: Defaults to `InMemoryRepository` (`app/database/repository.py`).
- **Pipeline Orchestration**: Uses FastAPI `BackgroundTasks` to coordinate extraction and verification without expensive infrastructure.

