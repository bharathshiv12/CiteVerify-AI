# System Architecture & Component Design

This document details the software architecture, data flow, component boundaries, and technology decisions for CiteVerify AI.

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Frontend["Frontend Layer (Next.js 14 App Router)"]
        UI_Landing["Landing & PDF Upload Dropzone"]
        UI_Status["Polling Processing Screen"]
        UI_Dashboard["Verification Dashboard & Report"]
        UI_Review["Human Review Modal"]
        Client_API["API Client (services/api.ts)"]
    end

    subgraph Backend["Backend Layer (FastAPI Monolith)"]
        API_Gateway["FastAPI App (app/main.py)"]
        MW["Request-ID, Logging & CORS Middleware"]
        Val["Upload Validator (magic bytes %PDF-)"]
        BG["FastAPI BackgroundTasks Worker"]
        Repo["AbstractRepository (InMemory / SQLite / Postgres)"]
    end

    subgraph Libraries["In-Process Python Packages (Libraries)"]
        subgraph Research_Services["research_services/ Package"]
            RS_HTTP["Common HTTP Client (Polite Pool, Retry, Cache)"]
            RS_Crossref["Crossref API Client"]
            RS_OpenAlex["OpenAlex API Client"]
            RS_EuropePMC["Europe PMC Client"]
            RS_Matcher["Publication Matcher (Confidence Scoring)"]
            RS_Extractor["Evidence Extractor (EvidenceLevel Tagging)"]
        end

        subgraph AI_Engine["ai_engine/ Package"]
            AI_Claim["Claim Extractor (Empirical Assertion Prompt)"]
            AI_Embed["Embedding Service (Sentence-Transformers / API)"]
            AI_Rerank["Evidence Passage Reranker"]
            AI_Verify["Verification Engine (Structured LLM Inference)"]
            AI_LLM["LLM Provider Abstraction (Gemini / OpenAI / Local)"]
        end
    end

    subgraph External["External Public Infrastructure (₹0 Free Tier)"]
        Ext_Crossref["Crossref REST API (Polite Pool)"]
        Ext_OpenAlex["OpenAlex REST API (Polite Pool)"]
        Ext_EuropePMC["Europe PMC REST API"]
        Ext_LLM["Google Gemini API (Free Tier)"]
    end

    %% Flow connections
    UI_Landing -->|POST /api/documents/upload| API_Gateway
    UI_Status -->|GET /api/documents/{id}/status| API_Gateway
    UI_Dashboard -->|GET /api/documents/{id}/report| API_Gateway
    UI_Review -->|POST /api/claims/{id}/review| API_Gateway

    API_Gateway --> MW
    MW --> Val
    Val --> Repo
    API_Gateway -->|Enqueue| BG

    BG -->|Extracts Text & Citations| Backend
    BG -->|Calls directly as Python library| Research_Services
    BG -->|Calls directly as Python library| AI_Engine

    RS_Crossref --> Ext_Crossref
    RS_OpenAlex --> Ext_OpenAlex
    RS_EuropePMC --> Ext_EuropePMC
    AI_LLM --> Ext_LLM

    AI_Verify --> Repo
    Repo --> UI_Dashboard
```

---

## 2. Key Architectural Decisions

### 2.1. In-Process Python Libraries vs. Microservices
- **Decision:** `ai_engine/` and `research_services/` are structured as importable Python library packages, called directly by the FastAPI backend within the same Python process.
- **Rationale for 24-Hour Hackathon:**
  - Microservices introduce port conflicts, docker networking issues, JSON serialization overhead, and distributed failure modes.
  - An in-process library model provides single-command local development (`uvicorn app.main:app`), zero network latency between components, and shared typed memory objects.

### 2.2. Zero-Dependency Repository Interface
- **Decision:** Persistence is abstracted behind `AbstractRepository` (`app/database/repository.py`), defaulting to `InMemoryRepository` (or SQLite).
- **Rationale:**
  - Developers can immediately clone and run the full stack without needing local PostgreSQL installed, Docker running, or cloud Supabase credentials configured.
  - When Supabase/PostgreSQL is connected later via `DATABASE_URL`, a `PostgresRepository` plugs seamlessly into the existing repository interface.

### 2.3. Asynchronous Pipeline via BackgroundTasks
- **Decision:** Use FastAPI's native `BackgroundTasks` for PDF processing, retrieval, and verification.
- **Rationale:**
  - Avoids introducing heavy task queues (Celery, Redis, RabbitMQ) that require external daemon processes.
  - The client uploads a PDF, receives `202 Accepted`, and polls `GET /api/documents/{id}/status` for live pipeline progress.

