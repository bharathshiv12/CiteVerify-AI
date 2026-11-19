-- ==============================================================================
-- CiteVerify AI — Supabase SQL Editor Master Script (000_all_in_one.sql)
-- Run this in your Supabase Dashboard SQL Editor to set up the complete schema,
-- Row-Level Security (RLS) policies, storage bucket, and performance indexes.
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ------------------------------------------------------------------------------
-- 1. Profiles Table (linked to Supabase auth.users)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    institution TEXT,
    role TEXT DEFAULT 'authenticated',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name, institution, role)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'institution', ''),
        'authenticated'
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ------------------------------------------------------------------------------
-- 2. Documents Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_size_bytes INT NOT NULL,
    mime_type VARCHAR(50) NOT NULL DEFAULT 'application/pdf',
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    pipeline_stage VARCHAR(50) NOT NULL DEFAULT 'UPLOADED',
    page_count INT,
    is_scanned BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    storage_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_document_status CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')),
    CONSTRAINT chk_document_stage CHECK (pipeline_stage IN (
        'UPLOADED', 'TEXT_EXTRACTION', 'CLAIM_EXTRACTION', 'CITATION_PARSING',
        'REFERENCE_PARSING', 'CITATION_MATCHING', 'PAPER_RETRIEVAL',
        'EVIDENCE_EXTRACTION', 'VERIFICATION', 'REPORT_GENERATION', 'DONE'
    ))
);

-- ------------------------------------------------------------------------------
-- 3. Research Papers Table (Shared Reference Cache)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.research_papers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doi VARCHAR(255) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT[] DEFAULT '{}',
    year INT,
    venue VARCHAR(255),
    abstract TEXT,
    is_open_access BOOLEAN DEFAULT FALSE,
    open_access_url TEXT,
    pdf_url TEXT,
    provider VARCHAR(50) NOT NULL,
    retrieval_status VARCHAR(50) NOT NULL,
    match_confidence REAL NOT NULL DEFAULT 0.0,
    match_reason TEXT,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_retrieval_status CHECK (retrieval_status IN ('RETRIEVED', 'NOT_FOUND', 'PAYWALLED', 'API_ERROR'))
);

-- ------------------------------------------------------------------------------
-- 4. Citations Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    raw_marker VARCHAR(100) NOT NULL,
    marker_type VARCHAR(50) NOT NULL,
    page_number INT NOT NULL,
    char_span INT[],
    reference_text TEXT,
    reference_index INT,
    matched_paper_id UUID REFERENCES public.research_papers(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_marker_type CHECK (marker_type IN ('NUMERIC', 'AUTHOR_YEAR'))
);

-- ------------------------------------------------------------------------------
-- 5. Claims Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.claims (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    page_number INT NOT NULL,
    char_span INT[] NOT NULL,
    verdict VARCHAR(50),
    verification_state VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    confidence REAL NOT NULL DEFAULT 0.0,
    rationale TEXT NOT NULL DEFAULT '',
    needs_human_review BOOLEAN NOT NULL DEFAULT FALSE,
    review_reasons TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_claim_verdict CHECK (verdict IS NULL OR verdict IN (
        'SUPPORTED', 'PARTLY_SUPPORTED', 'UNSUPPORTED', 'CONTRADICTORY', 'POTENTIALLY_OUTDATED'
    )),
    CONSTRAINT chk_verification_state CHECK (verification_state IN (
        'VERIFIED', 'REQUIRES_HUMAN_REVIEW', 'UNABLE_TO_VERIFY', 'PENDING'
    ))
);

-- ------------------------------------------------------------------------------
-- 6. Claim Citations (Many-to-Many Bridge)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.claim_citations (
    claim_id UUID NOT NULL REFERENCES public.claims(id) ON DELETE CASCADE,
    citation_id UUID NOT NULL REFERENCES public.citations(id) ON DELETE CASCADE,
    link_method VARCHAR(50) DEFAULT 'proximity',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (claim_id, citation_id)
);

-- ------------------------------------------------------------------------------
-- 7. Evidence Passages Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paper_id UUID REFERENCES public.research_papers(id) ON DELETE CASCADE,
    claim_id UUID REFERENCES public.claims(id) ON DELETE CASCADE,
    source_provider VARCHAR(50) NOT NULL,
    doi VARCHAR(255),
    url TEXT,
    passage TEXT NOT NULL,
    evidence_level VARCHAR(50) NOT NULL,
    retrieval_status VARCHAR(50) NOT NULL,
    similarity_score REAL,
    section_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_evidence_level CHECK (evidence_level IN ('FULL_TEXT', 'ABSTRACT_ONLY', 'METADATA_ONLY', 'NONE')),
    CONSTRAINT chk_evidence_retrieval CHECK (retrieval_status IN ('RETRIEVED', 'NOT_FOUND', 'PAYWALLED', 'API_ERROR'))
);

-- ------------------------------------------------------------------------------
-- 8. Verifications Table (Audit History of Evaluations)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES public.claims(id) ON DELETE CASCADE,
    verdict VARCHAR(50),
    verification_state VARCHAR(50) NOT NULL,
    confidence REAL NOT NULL DEFAULT 0.0,
    rationale TEXT NOT NULL DEFAULT '',
    evidence_summary TEXT,
    needs_human_review BOOLEAN NOT NULL DEFAULT FALSE,
    review_reasons TEXT[] DEFAULT '{}',
    method VARCHAR(50) DEFAULT 'heuristic_rule_engine',
    is_latest BOOLEAN DEFAULT TRUE,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 9. Human Reviews Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.human_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    claim_id UUID NOT NULL REFERENCES public.claims(id) ON DELETE CASCADE,
    reviewer_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    reviewer_name VARCHAR(255) NOT NULL,
    previous_verdict VARCHAR(50),
    updated_verdict VARCHAR(50) NOT NULL,
    notes TEXT NOT NULL,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_review_verdict CHECK (updated_verdict IN (
        'SUPPORTED', 'PARTLY_SUPPORTED', 'UNSUPPORTED', 'CONTRADICTORY', 'POTENTIALLY_OUTDATED'
    ))
);

-- ------------------------------------------------------------------------------
-- 10. Reports Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    total_claims INT NOT NULL DEFAULT 0,
    reliability_score REAL NOT NULL DEFAULT 0.0,
    verdict_counts JSONB NOT NULL DEFAULT '{}'::jsonb,
    evidence_level_counts JSONB NOT NULL DEFAULT '{}'::jsonb,
    human_review_required_count INT NOT NULL DEFAULT 0,
    claims_snapshot JSONB NOT NULL DEFAULT '[]'::jsonb,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 11. Processing Jobs Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.processing_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    current_stage VARCHAR(50) NOT NULL DEFAULT 'UPLOADED',
    progress_percent INT NOT NULL DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_job_status CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'))
);

-- ------------------------------------------------------------------------------
-- 12. User Settings Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_settings (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    notify_analysis_done BOOLEAN NOT NULL DEFAULT TRUE,
    notify_human_review_needed BOOLEAN NOT NULL DEFAULT TRUE,
    preferred_research_provider VARCHAR(50) NOT NULL DEFAULT 'ALL',
    strict_numeric_comparison BOOLEAN NOT NULL DEFAULT TRUE,
    auto_flag_outdated_years INT NOT NULL DEFAULT 10,
    allow_external_ai_evaluation BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 13. Activity Log Table
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- 14. Timestamp Triggers
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_documents_updated_at ON public.documents;
CREATE TRIGGER trg_documents_updated_at BEFORE UPDATE ON public.documents
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS trg_claims_updated_at ON public.claims;
CREATE TRIGGER trg_claims_updated_at BEFORE UPDATE ON public.claims
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS trg_processing_jobs_updated_at ON public.processing_jobs;
CREATE TRIGGER trg_processing_jobs_updated_at BEFORE UPDATE ON public.processing_jobs
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- ------------------------------------------------------------------------------
-- 15. Row-Level Security (RLS) Policies
-- ------------------------------------------------------------------------------
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.research_papers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claims ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.claim_citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.human_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;

-- Profiles
DROP POLICY IF EXISTS "Users can read own profile" ON public.profiles;
CREATE POLICY "Users can read own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Documents
DROP POLICY IF EXISTS "Users can select own documents" ON public.documents;
CREATE POLICY "Users can select own documents" ON public.documents FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own documents" ON public.documents;
CREATE POLICY "Users can insert own documents" ON public.documents FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own documents" ON public.documents;
CREATE POLICY "Users can update own documents" ON public.documents FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can delete own documents" ON public.documents;
CREATE POLICY "Users can delete own documents" ON public.documents FOR DELETE USING (auth.uid() = user_id);

-- Research Papers (Shared reference cache)
DROP POLICY IF EXISTS "Authenticated users can read research papers" ON public.research_papers;
CREATE POLICY "Authenticated users can read research papers" ON public.research_papers FOR SELECT TO authenticated USING (true);

-- Citations
DROP POLICY IF EXISTS "Users can read citations of own documents" ON public.citations;
CREATE POLICY "Users can read citations of own documents" ON public.citations FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = citations.document_id AND d.user_id = auth.uid()
));
DROP POLICY IF EXISTS "Users can insert citations to own documents" ON public.citations;
CREATE POLICY "Users can insert citations to own documents" ON public.citations FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = citations.document_id AND d.user_id = auth.uid()
));
DROP POLICY IF EXISTS "Users can delete citations of own documents" ON public.citations;
CREATE POLICY "Users can delete citations of own documents" ON public.citations FOR DELETE USING (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = citations.document_id AND d.user_id = auth.uid()
));

-- Claims
DROP POLICY IF EXISTS "Users can read claims of own documents" ON public.claims;
CREATE POLICY "Users can read claims of own documents" ON public.claims FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = claims.document_id AND d.user_id = auth.uid()
));
DROP POLICY IF EXISTS "Users can insert claims to own documents" ON public.claims;
CREATE POLICY "Users can insert claims to own documents" ON public.claims FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = claims.document_id AND d.user_id = auth.uid()
));
DROP POLICY IF EXISTS "Users can update claims of own documents" ON public.claims;
CREATE POLICY "Users can update claims of own documents" ON public.claims FOR UPDATE USING (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = claims.document_id AND d.user_id = auth.uid()
));
DROP POLICY IF EXISTS "Users can delete claims of own documents" ON public.claims;
CREATE POLICY "Users can delete claims of own documents" ON public.claims FOR DELETE USING (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = claims.document_id AND d.user_id = auth.uid()
));

-- Claim Citations
DROP POLICY IF EXISTS "Users can read claim citations of own documents" ON public.claim_citations;
CREATE POLICY "Users can read claim citations of own documents" ON public.claim_citations FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.claims c JOIN public.documents d ON d.id = c.document_id WHERE c.id = claim_citations.claim_id AND d.user_id = auth.uid()
));

-- Evidence
DROP POLICY IF EXISTS "Users can read evidence of own claims" ON public.evidence;
CREATE POLICY "Users can read evidence of own claims" ON public.evidence FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.claims c JOIN public.documents d ON d.id = c.document_id WHERE c.id = evidence.claim_id AND d.user_id = auth.uid()
));

-- Verifications
DROP POLICY IF EXISTS "Users can read verifications of own claims" ON public.verifications;
CREATE POLICY "Users can read verifications of own claims" ON public.verifications FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.claims c JOIN public.documents d ON d.id = c.document_id WHERE c.id = verifications.claim_id AND d.user_id = auth.uid()
));

-- Human Reviews
DROP POLICY IF EXISTS "Users can read human reviews of own claims" ON public.human_reviews;
CREATE POLICY "Users can read human reviews of own claims" ON public.human_reviews FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.claims c JOIN public.documents d ON d.id = c.document_id WHERE c.id = human_reviews.claim_id AND d.user_id = auth.uid()
));
DROP POLICY IF EXISTS "Users can insert human reviews for own claims" ON public.human_reviews;
CREATE POLICY "Users can insert human reviews for own claims" ON public.human_reviews FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM public.claims c JOIN public.documents d ON d.id = c.document_id WHERE c.id = human_reviews.claim_id AND d.user_id = auth.uid()
));

-- Reports
DROP POLICY IF EXISTS "Users can read reports of own documents" ON public.reports;
CREATE POLICY "Users can read reports of own documents" ON public.reports FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = reports.document_id AND d.user_id = auth.uid()
));
DROP POLICY IF EXISTS "Users can insert reports for own documents" ON public.reports;
CREATE POLICY "Users can insert reports for own documents" ON public.reports FOR INSERT WITH CHECK (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = reports.document_id AND d.user_id = auth.uid()
));

-- Processing Jobs
DROP POLICY IF EXISTS "Users can read processing jobs of own documents" ON public.processing_jobs;
CREATE POLICY "Users can read processing jobs of own documents" ON public.processing_jobs FOR SELECT USING (EXISTS (
    SELECT 1 FROM public.documents d WHERE d.id = processing_jobs.document_id AND d.user_id = auth.uid()
));

-- User Settings
DROP POLICY IF EXISTS "Users can read own settings" ON public.user_settings;
CREATE POLICY "Users can read own settings" ON public.user_settings FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own settings" ON public.user_settings;
CREATE POLICY "Users can update own settings" ON public.user_settings FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own settings" ON public.user_settings;
CREATE POLICY "Users can insert own settings" ON public.user_settings FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Activity Log
DROP POLICY IF EXISTS "Users can read own activity log" ON public.activity_log;
CREATE POLICY "Users can read own activity log" ON public.activity_log FOR SELECT USING (auth.uid() = user_id);

-- Storage bucket 'sapthack-documents'
INSERT INTO storage.buckets (id, name, public)
VALUES ('sapthack-documents', 'sapthack-documents', false)
ON CONFLICT (id) DO NOTHING;

DROP POLICY IF EXISTS "Users can upload document to own folder" ON storage.objects;
CREATE POLICY "Users can upload document to own folder" ON storage.objects FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'sapthack-documents' AND (storage.foldername(name))[1] = auth.uid()::text);

DROP POLICY IF EXISTS "Users can read documents from own folder" ON storage.objects;
CREATE POLICY "Users can read documents from own folder" ON storage.objects FOR SELECT TO authenticated
USING (bucket_id = 'sapthack-documents' AND (storage.foldername(name))[1] = auth.uid()::text);

DROP POLICY IF EXISTS "Users can delete documents from own folder" ON storage.objects;
CREATE POLICY "Users can delete documents from own folder" ON storage.objects FOR DELETE TO authenticated
USING (bucket_id = 'sapthack-documents' AND (storage.foldername(name))[1] = auth.uid()::text);

-- ------------------------------------------------------------------------------
-- 16. Indexes for Performance
-- ------------------------------------------------------------------------------
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
