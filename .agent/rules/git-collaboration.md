# Rule: Git Collaboration & Monorepo Discipline

This rule enforces clean, parallel development across 4 developer/agent pairs.

---

## 1. Branch Strategy
- `main`: Protected production-ready branch. Must always pass tests and contract validation.
- Long-lived feature branches:
  - `feature/frontend` (Agent 1)
  - `feature/backend` (Agent 2)
  - `feature/ai-engine` (Agent 3)
  - `feature/research-api` (Agent 4)
- Short-lived topic branches (e.g. `feature/backend-pdf-upload`) may be branched off the role feature branch.

---

## 2. Commit Message Standard
Follow Conventional Commits: `type(scope): concise description`
- `feat(claim-extractor)`: add few-shot prompt for empirical claims
- `fix(upload)`: reject corrupt magic bytes
- `test(contracts)`: add schema synchronization test
- `docs(roadmap)`: update hour 6 milestone deliverables
- `chore(deps)`: update development dependencies

---

## 3. Pull Request Requirements
- Complete the PR template checklist:
  - Contract unchanged or linked contract PR approved.
  - Pytest / frontend build passes.
  - No credentials, secrets, or `.env` files tracked.
  - No modifications to files outside assigned role ownership.
- Rebase frequently on `origin/main` to avoid large merge conflicts.

