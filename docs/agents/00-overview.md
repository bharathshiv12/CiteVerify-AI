# 00. Agent Team Overview & Architecture

CiteVerify AI is developed concurrently by four autonomous agent/developer pairs operating within a unified monorepo.

---

## 1. Team Roster & Module Ownership

| Role | Agent ID | Core Directory | Branch | Key Deliverable |
|---|---|---|---|---|
| **Frontend Developer** | Agent 1 | `frontend/**` | `feature/frontend` | Upload UI, verification dashboard, claim viewer, report screen |
| **Backend Architect** | Agent 2 | `backend/**`, `scripts/**` | `feature/backend` | PDF processor, pipeline orchestrator, DB repository, API endpoints |
| **AI/ML Engineer** | Agent 3 | `ai_engine/**` | `feature/ai-engine` | Claim extraction, vector embeddings, LLM verification reasoning |
| **Research Integration** | Agent 4 | `research_services/**`, `tests/integration/**` | `feature/research-api` | Crossref/OpenAlex/Europe PMC clients, publication matcher |

---

## 2. In-Process Library Architecture (Simple & Robust)

To eliminate network overhead, port sprawl, and multi-service orchestration bugs in a 24-hour hackathon, `ai_engine` and `research_services` are **Python library packages** imported directly by the backend:

```
[ Frontend (Next.js) ]
         │ (HTTP / JSON)
         ▼
[ Backend (FastAPI Orchestrator) ]
         ├── calls ──> [ research_services (Python package) ]
         └── calls ──> [ ai_engine (Python package) ]
```

---

## 3. Communication Protocols
- Shared data contracts in `contracts/` are the definitive source of truth.
- Contract updates require a dedicated `contract-change` PR approved by all 4 roles.
- `scripts/validate_repo.py` acts as the gatekeeper in local development and CI.

