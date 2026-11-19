# CiteVerify AI - AI & Machine Learning Engine

This package handles claim extraction, vector ranking, and natural language inference verification for CiteVerify AI.

---

## 1. Responsibilities & Ownership
- **Owner:** Agent 3 (AI/ML Engineer)
- **Role:** Implements factual claim extraction, passage reranking, and verification reasoning.

---

## 2. Directory Structure
```
ai_engine/
├── claim_extractor/      # Extracts factual assertions from paper text
├── citation_matcher/     # Assists in mapping claims to adjacent citations
├── embedding_service/    # Computes cosine similarity vector scores
├── evidence_retriever/   # Reranks and filters candidate evidence passages
├── verification_engine/  # LLM natural language inference against evidence
├── llm/                  # Provider-agnostic LLM client (Gemini / OpenAI / Local)
├── prompts/              # Versioned prompt templates (not hardcoded strings)
├── schemas/              # Reuses canonical Pydantic schemas
├── training/             # OPTIONAL ML fine-tuning experiments and notebooks
├── evaluation/           # Evaluation script computing accuracy/F1 per verdict
├── data/                 # Hand-labeled test samples for verification benchmarking
└── models/               # Model weights documentation (weights gitignored)
```

---

## 3. LLM Provider Configuration
Set in `ai_engine/.env` or root `.env`:
- `LLM_PROVIDER`: `gemini` (Default), `openai`, or `local`.
- `LLM_API_KEY`: API key for Google Gemini free tier.
- `LLM_MODEL`: `gemini-1.5-flash` or `gemini-2.0-flash`.

