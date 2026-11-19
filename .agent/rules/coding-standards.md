# Rule: Coding Standards & Best Practices

All code committed to CiteVerify AI must comply with the following standards:

---

## 1. Python Code Standards (Backend, AI Engine, Research Services)
- **Formatting & Style:** PEP 8 compliance, 4-space indentation, explicit type hints on all functions and methods.
- **Python Version Compatibility:** Python 3.13+ target. Avoid relying on deprecated features.
- **Schema Validation:** Use Pydantic v2 `BaseModel` with `ConfigDict(from_attributes=True)`. Do not use Pydantic v1 `class Config`.
- **Package Imports:** Relative imports within packages, absolute imports across top-level packages (`backend`, `ai_engine`, `research_services`).
- **Error Handling:** Avoid bare `except:`. Raise specific `AppException` subclasses (`NotFoundError`, `InvalidFileError`, etc.).
- **Async Safety:** Non-blocking I/O for all external network requests (use `httpx.AsyncClient`).

---

## 2. TypeScript & Frontend Standards
- **Strict Mode:** TypeScript `strict: true` enabled; no untyped `any` without an explicit justification comment.
- **Naming Conventions:**
  - TypeScript interfaces matching API responses use `snake_case` keys directly.
  - Component filenames use PascalCase (e.g. `ClaimCard.tsx`).
  - Utility and hook functions use camelCase (e.g. `useDocumentStatus.ts`).
- **Framework Conventions:** Next.js 14 App Router, Client Components marked with `"use client"` at top.
- **Accessibility:** Semantic HTML elements (`<main>`, `<section>`, `<header>`, `<article>`), visible focus indicators, descriptive `aria-label`s on buttons.

---

## 3. Security & Environment
- Never hardcode secrets, API keys, passwords, or personal emails.
- Read credentials strictly from environment variables.
- Service-role database keys and LLM keys must reside on the backend; never expose them to frontend client code (`NEXT_PUBLIC_*`).

