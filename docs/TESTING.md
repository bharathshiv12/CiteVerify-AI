# Testing Strategy & Quality Assurance Guide

CiteVerify AI employs a multi-tiered test suite ensuring schema contracts, input validators, and inference pipelines remain robust throughout the 24-hour hackathon.

---

## 1. Test Architecture

```
tests/
├── integration/              # Cross-module integration tests
├── end_to_end/               # Full pipeline runs against sample papers
└── sample_documents/         # Guide and metadata for open-access test papers
backend/tests/
├── test_health.py            # Liveness probe test
├── test_contract.py          # Contract enum synchronization test
└── test_upload_validation.py # PDF magic byte, size, MIME validation tests
```

---

## 2. Running Test Suites

### 2.1. Backend Unit & Contract Tests
```bash
# Git Bash
backend/.venv/Scripts/python -m pytest backend/tests -v

# PowerShell
backend\.venv\Scripts\python.exe -m pytest backend/tests -v
```

### 2.2. Whole-Repo Contract Validation
Runs schema syntax checks and verifies enum parity across `enums.json`, Pydantic models, and TypeScript types:
```bash
python scripts/validate_repo.py
```

### 2.3. Frontend Type & Build Verification
```bash
npm --prefix frontend run build
```

---

## 3. Real Test Data & No-Fabrication Rule

> [!CAUTION]
> **Never commit proprietary, private, or fabricated academic papers to this repository.**
> Synthetic mock data in `contracts/examples/` is explicitly tagged `_synthetic: true` and used only for isolated UI styling.

### How to Obtain Real Open-Access Test Papers:
1. Use papers with open Creative Commons licenses (`CC BY 4.0`):
   - **arXiv.org:** e.g., Vaswani et al., *"Attention Is All You Need"* (arXiv:1706.03762).
   - **PLOS ONE / BioMed Central:** Fully open-access biomedical literature.
   - **Europe PMC Open Access Subset:** Query papers with open-access flags.
2. Download the official PDF from the publisher repository into `tests/sample_documents/` locally for manual end-to-end testing (gitignored by default).

