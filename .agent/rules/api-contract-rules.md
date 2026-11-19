# Rule: API Contract Governance

The API contract defines the operational boundaries and expectations between frontend, backend, AI engine, and research modules.

---

## 1. Single Source of Truth Hierarchy
1. Canonical contract files:
   - `contracts/openapi/openapi.yaml`
   - `contracts/schemas/enums.json`
   - `contracts/schemas/*.schema.json`
2. Derived implementation files:
   - `backend/app/schemas/*.py`
   - `frontend/types/*.ts`

---

## 2. Prohibition on Ad-hoc Field Creation
- No agent or developer may invent, rename, or delete fields without updating canonical contracts first.
- If a new feature requires an extra field:
  1. Open a `contract-change` issue.
  2. Update `contracts/openapi/openapi.yaml` and `contracts/schemas/*.schema.json`.
  3. Update `backend/app/schemas/` and `frontend/types/`.
  4. Run `python scripts/validate_repo.py` to ensure schema synchronization.
  5. Merge the contract update before implementing feature logic.

---

## 3. Envelope Conventions
- **Success Collections:** Must use list envelope:
  ```json
  { "items": [], "page": 1, "page_size": 20, "total": 0 }
  ```
- **Error Responses:** Must use error envelope:
  ```json
  { "error": { "code": "...", "message": "...", "details": {}, "request_id": "..." } }
  ```

