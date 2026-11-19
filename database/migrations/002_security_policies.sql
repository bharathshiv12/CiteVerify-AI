-- ==============================================================================
-- CiteVerify AI — Migration 002: Security Policies & Row Level Security (RLS)
-- ==============================================================================

-- Enable RLS on all tables
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

-- 1. Profiles Policies
CREATE POLICY "Users can read own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- 2. Documents Policies (Owner isolation)
CREATE POLICY "Users can select own documents"
    ON public.documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents"
    ON public.documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own documents"
    ON public.documents FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own documents"
    ON public.documents FOR DELETE
    USING (auth.uid() = user_id);

-- 3. Research Papers Policies (Shared reference data)
CREATE POLICY "Authenticated users can read research papers"
    ON public.research_papers FOR SELECT
    TO authenticated
    USING (true);

-- Research papers are modified only via service role (backend worker)

-- 4. Citations Policies (Inherited from owning document)
CREATE POLICY "Users can read citations of own documents"
    ON public.citations FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = citations.document_id AND d.user_id = auth.uid()
    ));

CREATE POLICY "Users can insert citations to own documents"
    ON public.citations FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = citations.document_id AND d.user_id = auth.uid()
    ));

CREATE POLICY "Users can delete citations of own documents"
    ON public.citations FOR DELETE
    USING (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = citations.document_id AND d.user_id = auth.uid()
    ));

-- 5. Claims Policies (Inherited from owning document)
CREATE POLICY "Users can read claims of own documents"
    ON public.claims FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = claims.document_id AND d.user_id = auth.uid()
    ));

CREATE POLICY "Users can insert claims to own documents"
    ON public.claims FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = claims.document_id AND d.user_id = auth.uid()
    ));

CREATE POLICY "Users can update claims of own documents"
    ON public.claims FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = claims.document_id AND d.user_id = auth.uid()
    ));

CREATE POLICY "Users can delete claims of own documents"
    ON public.claims FOR DELETE
    USING (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = claims.document_id AND d.user_id = auth.uid()
    ));

-- 6. Claim Citations Policies
CREATE POLICY "Users can read claim citations of own documents"
    ON public.claim_citations FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.claims c
        JOIN public.documents d ON d.id = c.document_id
        WHERE c.id = claim_citations.claim_id AND d.user_id = auth.uid()
    ));

-- 7. Evidence Policies
CREATE POLICY "Users can read evidence of own claims"
    ON public.evidence FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.claims c
        JOIN public.documents d ON d.id = c.document_id
        WHERE c.id = evidence.claim_id AND d.user_id = auth.uid()
    ));

-- 8. Verifications Policies
CREATE POLICY "Users can read verifications of own claims"
    ON public.verifications FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.claims c
        JOIN public.documents d ON d.id = c.document_id
        WHERE c.id = verifications.claim_id AND d.user_id = auth.uid()
    ));

-- 9. Human Reviews Policies
CREATE POLICY "Users can read human reviews of own claims"
    ON public.human_reviews FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.claims c
        JOIN public.documents d ON d.id = c.document_id
        WHERE c.id = human_reviews.claim_id AND d.user_id = auth.uid()
    ));

CREATE POLICY "Users can insert human reviews for own claims"
    ON public.human_reviews FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.claims c
        JOIN public.documents d ON d.id = c.document_id
        WHERE c.id = human_reviews.claim_id AND d.user_id = auth.uid()
    ));

-- 10. Reports Policies
CREATE POLICY "Users can read reports of own documents"
    ON public.reports FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = reports.document_id AND d.user_id = auth.uid()
    ));

CREATE POLICY "Users can insert reports for own documents"
    ON public.reports FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = reports.document_id AND d.user_id = auth.uid()
    ));

-- 11. Processing Jobs Policies
CREATE POLICY "Users can read processing jobs of own documents"
    ON public.processing_jobs FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = processing_jobs.document_id AND d.user_id = auth.uid()
    ));

-- 12. User Settings Policies
CREATE POLICY "Users can read own settings"
    ON public.user_settings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own settings"
    ON public.user_settings FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings"
    ON public.user_settings FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- 13. Activity Log Policies
CREATE POLICY "Users can read own activity log"
    ON public.activity_log FOR SELECT
    USING (auth.uid() = user_id);

-- Storage bucket setup and policy for 'sapthack-documents'
-- Objects stored under: {user_id}/{document_id}.pdf
INSERT INTO storage.buckets (id, name, public)
VALUES ('sapthack-documents', 'sapthack-documents', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Users can upload document to own folder"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (
        bucket_id = 'sapthack-documents' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "Users can read documents from own folder"
    ON storage.objects FOR SELECT
    TO authenticated
    USING (
        bucket_id = 'sapthack-documents' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );

CREATE POLICY "Users can delete documents from own folder"
    ON storage.objects FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'sapthack-documents' AND
        (storage.foldername(name))[1] = auth.uid()::text
    );
