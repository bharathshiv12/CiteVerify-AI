-- ==============================================================================
-- CiteVerify AI — Migration 003: Indexes for High Performance Querying
-- ==============================================================================

-- Foreign Key & Ownership Indexes
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON public.documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON public.documents(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_claims_document_id ON public.claims(document_id);
CREATE INDEX IF NOT EXISTS idx_claims_verdict ON public.claims(verdict);
CREATE INDEX IF NOT EXISTS idx_claims_needs_review ON public.claims(needs_human_review);
CREATE INDEX IF NOT EXISTS idx_claims_verification_state ON public.claims(verification_state);

CREATE INDEX IF NOT EXISTS idx_citations_document_id ON public.citations(document_id);
CREATE INDEX IF NOT EXISTS idx_citations_matched_paper_id ON public.citations(matched_paper_id);

CREATE INDEX IF NOT EXISTS idx_research_papers_doi ON public.research_papers(doi);
CREATE INDEX IF NOT EXISTS idx_research_papers_provider ON public.research_papers(provider);

CREATE INDEX IF NOT EXISTS idx_evidence_paper_id ON public.evidence(paper_id);
CREATE INDEX IF NOT EXISTS idx_evidence_claim_id ON public.evidence(claim_id);
CREATE INDEX IF NOT EXISTS idx_evidence_level ON public.evidence(evidence_level);

CREATE INDEX IF NOT EXISTS idx_verifications_claim_id ON public.verifications(claim_id);
CREATE INDEX IF NOT EXISTS idx_human_reviews_claim_id ON public.human_reviews(claim_id);

CREATE INDEX IF NOT EXISTS idx_reports_document_id ON public.reports(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_jobs_document_id ON public.processing_jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON public.activity_log(user_id, created_at DESC);
