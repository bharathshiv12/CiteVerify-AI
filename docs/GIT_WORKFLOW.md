# Git Collaboration & Workflow Guide

This document defines the team Git branching model, commit conventions, synchronization rules, and conflict resolution protocols for CiteVerify AI.

---

## 1. Branching Strategy

```
main (protected, always deployable)
  ├── feature/frontend    (Agent 1 / Frontend Dev)
  ├── feature/backend     (Agent 2 / Backend Dev)
  ├── feature/ai-engine   (Agent 3 / AI Engineer)
  └── feature/research-api (Agent 4 / Research Integration)
```

- **`main`:** The canonical production branch. Direct pushes to `main` are prohibited. All code merges into `main` via reviewed Pull Requests.
- **Role Feature Branches:** Each developer/agent pair maintains their own dedicated branch.
- **Short-Lived Topic Branches:** For isolated tasks, branch off your feature branch (e.g. `git checkout -b feature/backend-pdf-upload feature/backend`).

---

## 2. Commit Message Standards

We use the Conventional Commits specification:
```
type(scope): concise subject line in imperative mood
```

### Allowed Types:
- `feat`: A new user-facing feature or API endpoint.
- `fix`: A bug fix or error correction.
- `test`: Adding or updating test suites.
- `docs`: Documentation updates.
- `refactor`: Code reorganization without functional changes.
- `chore`: Dependency updates, build configs, formatting.

### Examples:
- `feat(upload): enforce %PDF- magic bytes validation`
- `fix(matcher): handle numeric citations with hyphenated ranges`
- `test(contracts): assert Pydantic enums match enums.json`
- `docs(roadmap): update hour 12 milestone deliverables`

---

## 3. Daily Workflow: Step-by-Step

### 3.1. Starting Work
```bash
# Sync local main with upstream
git checkout main
git pull --rebase

# Switch to your feature branch and rebase on main
git checkout feature/backend
git rebase main
```

### 3.2. Making Changes
```bash
# Stage only files in your owned directory
git add backend/app/services/document_processor.py
git commit -m "feat(processor): add text extraction with page tracking"
```

### 3.3. Opening a Pull Request
1. Ensure all local tests and repo validation scripts pass:
   ```bash
   python scripts/validate_repo.py
   backend/.venv/Scripts/pytest backend/tests -v
   ```
2. Open PR from `feature/<role>` into `main`.
3. Fill out `.github/pull_request_template.md`.

---

## 4. Conflict Resolution & Shared Files Policy

### What if two developers need the same file?
1. **Shared Contract Rule:** If the conflict is in `contracts/**`, `backend/app/schemas/**`, or `frontend/types/**`, stop immediately. Raise a `contract-change` issue. Both developers must agree on the schema before anyone writes code.
2. **Rebasing Protocol:** When rebasing on `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   # If conflicts occur:
   git status  # Inspect conflicting files
   # Resolve conflicts manually
   git add <resolved-file>
   git rebase --continue
   ```
3. Never use `git push --force` on shared branches. Use `--force-with-lease` if necessary on personal topic branches only.

