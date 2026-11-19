/**
 * Canonical domain interfaces matching contracts/schemas/*.schema.json.
 * All property keys use snake_case to preserve exact parity with backend responses.
 */

import {
  VerificationVerdict,
  ProcessingStatus,
  VerificationState,
  EvidenceLevel,
  RetrievalStatus,
  PipelineStage,
} from './enums';

export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  request_id: string;
}

export interface ErrorEnvelope {
  error: ErrorDetail;
}

export interface Document {
  id: string;
  filename: string;
  file_size_bytes: number;
  mime_type: string;
  status: ProcessingStatus;
  pipeline_stage: PipelineStage;
  page_count: number | null;
  is_scanned: boolean;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentStatusResponse {
  document_id: string;
  status: ProcessingStatus;
  pipeline_stage: PipelineStage;
  progress_percent: number;
  total_claims_found: number;
  verified_claims_count: number;
  error_message: string | null;
}

export interface DocumentAnalyzeResponse {
  document_id: string;
  status: ProcessingStatus;
  pipeline_stage: PipelineStage;
  message: string;
}

export interface Citation {
  id: string;
  document_id: string;
  raw_marker: string;
  marker_type: 'NUMERIC' | 'AUTHOR_YEAR';
  page_number: number;
  char_span?: [number, number];
  reference_text?: string | null;
  reference_index?: number | null;
  matched_paper_id?: string | null;
}

export interface ResearchPaper {
  id: string;
  doi?: string | null;
  title: string;
  authors: string[];
  year?: number | null;
  venue?: string | null;
  abstract?: string | null;
  is_open_access: boolean;
  open_access_url?: string | null;
  pdf_url?: string | null;
  provider: string;
  retrieval_status: RetrievalStatus;
  match_confidence: number;
  match_reason?: string | null;
  retrieved_at: string;
}

export interface Evidence {
  id: string;
  paper_id?: string | null;
  source_provider: string;
  doi?: string | null;
  url?: string | null;
  passage: string;
  evidence_level: EvidenceLevel;
  retrieval_status: RetrievalStatus;
  similarity_score?: number | null;
  section_name?: string | null;
}

export interface Claim {
  id: string;
  document_id: string;
  claim_text: string;
  page_number: number;
  char_span: [number, number];
  citations: Citation[];
  verdict: VerificationVerdict | null;
  verification_state: VerificationState;
  confidence: number;
  rationale: string;
  evidence: Evidence[];
  needs_human_review: boolean;
  review_reasons: string[];
  created_at?: string;
  updated_at?: string;
}

export interface ClaimListResponse {
  items: Claim[];
  page: number;
  page_size: number;
  total: number;
}

export interface ClaimReviewRequest {
  reviewer_name: string;
  updated_verdict: VerificationVerdict;
  notes: string;
}

export interface VerificationReport {
  document_id: string;
  filename: string;
  generated_at: string;
  total_claims: number;
  reliability_score: number;
  verdict_counts: {
    SUPPORTED: number;
    PARTLY_SUPPORTED: number;
    UNSUPPORTED: number;
    CONTRADICTORY: number;
    POTENTIALLY_OUTDATED: number;
    UNVERIFIED: number;
  };
  evidence_level_counts: {
    FULL_TEXT: number;
    ABSTRACT_ONLY: number;
    METADATA_ONLY: number;
    NONE: number;
  };
  human_review_required_count: number;
  claims: Claim[];
}

export interface PaginatedDocuments {
  items: Document[];
  page: number;
  page_size: number;
  total: number;
}

export interface DashboardStats {
  total_documents: number;
  total_claims: number;
  supported_claims: number;
  partly_supported_claims: number;
  unsupported_claims: number;
  contradictory_claims: number;
  outdated_claims: number;
  needs_review_claims: number;
  average_reliability_score: number;
}

