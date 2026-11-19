# CiteVerify AI Contracts

This directory serves as the **Single Source of Truth (SSOT)** for all data structures, enumerations, API endpoints, and validation envelopes across CiteVerify AI.

---

## 1. Hierarchy of Truth

1. **`contracts/openapi/openapi.yaml` & `contracts/schemas/enums.json`**: The canonical definitions.
2. **`contracts/schemas/*.schema.json`**: JSON Schema (draft 2020-12) specifications for each domain model.
3. **`backend/app/schemas/`**: Pydantic v2 schemas directly derived from and matching canonical schemas.
4. **`frontend/types/`**: TypeScript interfaces directly matching canonical schemas (preserving `snake_case` property names).

> [!IMPORTANT]
> **No team member or agent may invent, rename, or drop fields independently.**
> Any contract modification requires an explicit `contract-change` issue/pull request with approval across all 4 roles before code changes can be merged.

---

## 2. Directory Structure

```
contracts/
├── openapi/
│   └── openapi.yaml           # Canonical OpenAPI 3.1.0 specification
├── schemas/
│   ├── enums.json             # Canonical enumerations
│   ├── error.schema.json      # Error envelope schema
│   ├── document.schema.json   # Document upload & metadata schema
│   ├── citation.schema.json   # In-text citation & reference schema
│   ├── research_paper.schema.json # Retrieved publication schema
│   ├── evidence.schema.json   # Extracted passage & evidence level schema
│   ├── verification.schema.json # Claim verification evaluation schema
│   ├── claim.schema.json      # Extracted claim with attached citations & evidence
│   └── report.schema.json     # Final synthesized verification report
├── examples/                  # SYNTHETIC fixture payloads for testing/mocks ONLY
│   ├── synthetic_document.json
│   ├── synthetic_claims.json
│   └── synthetic_report.json
└── README.md
```

---

## 3. Mock Data & Synthetic Payloads Rule

All synthetic fixtures reside strictly in `contracts/examples/`. Every synthetic payload contains:
- `"_synthetic": true`
- Obviously simulated titles and DOIs (e.g. `10.0000/synthetic.001`).

Frontend applications may only load synthetic data when `NEXT_PUBLIC_USE_MOCKS=true`, which must display a prominent, visible **"SAMPLE DATA"** banner. Mock data must never be loaded in production builds or live judging evaluations.

---

## 4. Contract Validation

The repository includes a validation script at `scripts/validate_repo.py` that verifies:
- All required JSON schemas and OpenAPI YAML files parse without syntax errors.
- Enums in `contracts/schemas/enums.json` are identical to backend Pydantic enums and frontend TypeScript enums.
- Synthetic mock payloads conform to the schema definitions.

