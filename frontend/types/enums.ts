/**
 * Canonical enumeration types matching contracts/schemas/enums.json.
 */

export type VerificationVerdict =
  | 'SUPPORTED'
  | 'PARTLY_SUPPORTED'
  | 'UNSUPPORTED'
  | 'CONTRADICTORY'
  | 'POTENTIALLY_OUTDATED';

export type ProcessingStatus =
  | 'PENDING'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'FAILED';

export type VerificationState =
  | 'VERIFIED'
  | 'REQUIRES_HUMAN_REVIEW'
  | 'UNABLE_TO_VERIFY'
  | 'PENDING';

export type EvidenceLevel =
  | 'FULL_TEXT'
  | 'ABSTRACT_ONLY'
  | 'METADATA_ONLY'
  | 'NONE';

export type RetrievalStatus =
  | 'RETRIEVED'
  | 'NOT_FOUND'
  | 'PAYWALLED'
  | 'API_ERROR';

export type PipelineStage =
  | 'UPLOADED'
  | 'TEXT_EXTRACTION'
  | 'CLAIM_EXTRACTION'
  | 'CITATION_PARSING'
  | 'REFERENCE_PARSING'
  | 'CITATION_MATCHING'
  | 'PAPER_RETRIEVAL'
  | 'EVIDENCE_EXTRACTION'
  | 'VERIFICATION'
  | 'REPORT_GENERATION'
  | 'DONE';

