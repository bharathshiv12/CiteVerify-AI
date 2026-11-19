# Team Ownership & Codeowners Matrix

This matrix governs repository change approvals, folder ownership, and PR merge permissions.

---

## 1. Directory Ownership Matrix

| Folder / Path | Primary Owner | Secondary Reviewer | Change Policy |
|---|---|---|---|
| `frontend/**` | Agent 1 (Frontend) | Agent 2 (Backend) | Frontend feature branch |
| `backend/**` | Agent 2 (Backend) | Agent 1 (Frontend) | Backend feature branch |
| `scripts/**` | Agent 2 (Backend) | Team Lead | Backend feature branch |
| `ai_engine/**` | Agent 3 (AI/ML) | Agent 2 (Backend) | AI feature branch |
| `research_services/**` | Agent 4 (Research) | Agent 2 (Backend) | Research feature branch |
| `tests/integration/**` | Agent 4 (Research) | Agent 2 (Backend) | Integration feature branch |
| `contracts/**` | **All 4 Agents** | Integration Lead | Dedicated `contract-change` PR requiring 4 approvals |
| `docs/**` | **All 4 Agents** | Integration Lead | Documentation update PR |
| `.agent/**` | **All 4 Agents** | Integration Lead | Agent configuration PR |
| `.github/**` | Agent 2 (DevOps) | Integration Lead | CI/CD update PR |

---

## 2. Integration Lead
- **Assigned Role:** Integration Lead (Team to populate username: `TODO_INTEGRATION_LEAD`)
- **Authority:** Resolves cross-boundary ambiguities, merges PRs into `main`, and oversees `scripts/validate_repo.py` in CI.

