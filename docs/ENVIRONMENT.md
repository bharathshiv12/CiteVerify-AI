# Environment Baseline and Tool Audit

**Date of Audit:** 2026-11-19  
**Platform:** Windows 11 (AMD64)  
**Shell Environment:** PowerShell / Git Bash  
**Workspace:** `c:\Users\BHARATH\Desktop\CiteVerify-AI`

---

## 1. System Tools & Runtimes

| Tool | Executable / Command | Detected Version | Available | Status / Compatibility Notes |
|---|---|---|---|---|
| **Python** | `python` | `Python 3.13.16` | **Yes** | Working primary command. `py` and `python3` not active. |
| **pip** | `python -m pip` | `pip 26.2.1` | **Yes** | Global site-packages contains only base tools (`pip`, `fonttools`). |
| **Git** | `git` | `git version 2.56.0.windows.2` | **Yes** | Fully available. Supports local branches, `.gitattributes`, LF normalization. |
| **Node.js** | `node` | `v24.22.1` | **Yes** | Node 24 Current. Compatible with Next.js (requires Node >= 18.18.0) and Vite. |
| **npm** | `npm` | `11.19.1` | **Yes** | Primary package manager for frontend dependencies. |
| **pnpm** | `pnpm` | *not found* | **No** | Use `npm` for all frontend package management. |
| **yarn** | `yarn` | *not found* | **No** | Use `npm`. |
| **Docker** | `docker` | *not found* | **No** | Optional for 24h MVP; local processes run directly on host. |
| **PostgreSQL** | `psql` | *not found* | **No** | In-memory/SQLite repository interface is default for zero-credential local dev. |

---

## 2. Python Packages Audit (Global Environment)

Output of `python -m pip list`:
- `fonttools` (4.68.0)
- `pip` (26.2.1)

Target backend/AI packages checked:
- `fastapi`: *not installed globally* (to be installed in `backend/.venv`)
- `uvicorn`: *not installed globally* (to be installed in `backend/.venv`)
- `pydantic`: *not installed globally* (to be installed in `backend/.venv`)
- `pytest`: *not installed globally* (to be installed in `backend/.venv`)
- `httpx`: *not installed globally* (to be installed in `backend/.venv`)
- `pymupdf`: *not installed globally* (optional text extraction in `backend/.venv`)
- `sentence-transformers`: *not installed globally*
- `torch`: *not installed globally*

---

## 3. Compatibility & Architecture Notes

1. **Python 3.13 Considerations:**
   - FastAPI, Pydantic v2, `pydantic-settings`, Uvicorn, and HTTPX run smoothly on Python 3.13.
   - Heavy ML frameworks such as PyTorch (`torch`) and `sentence-transformers` have historically trailed behind the latest Python minor releases on Windows. For the 24-hour hackathon MVP, the primary verification path uses the zero-shot LLM engine (e.g. Gemini API / OpenAI compatible) or API embeddings, making local PyTorch compilation strictly optional.
2. **Node.js v24 & Frontend:**
   - Node v24.22.1 satisfies Next.js 14/15 requirements (Node >= 18.18.0).
   - `npm` v11.19.1 will be used as the package manager.
3. **Isolation Rule:**
   - Global Python installation will remain untouched. All project dependencies must reside strictly inside isolated virtual environments (`backend/.venv`).
