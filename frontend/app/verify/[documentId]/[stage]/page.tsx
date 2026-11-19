"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "../../../../components/layout/app-shell";
import { ProgressTracker } from "../../../../components/verification/progress-tracker";
import { ClaimCard } from "../../../../components/verification/claim-card";
import { EvidencePanel } from "../../../../components/verification/evidence-panel";
import { HumanReviewPanel } from "../../../../components/verification/human-review-panel";
import { VerdictBadge, CitationBadge, EvidenceLevelBadge, RetrievalBadge } from "../../../../components/ui/status-badge";
import { ConfidenceIndicator } from "../../../../components/verification/confidence-indicator";
import { Button } from "../../../../components/ui/button";
import { SearchInput } from "../../../../components/ui/search-input";
import { Spinner, Skeleton } from "../../../../components/ui/spinner";
import { ErrorState } from "../../../../components/ui/error-state";
import { useDocumentStatus, useDocumentClaims, useDocumentReport } from "../../../../hooks/use-document";
import { Claim, VerificationVerdict, PipelineStage } from "../../../../types";
import {
  FileText,
  Search,
  ExternalLink,
  BookOpen,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ArrowRight,
  ArrowLeft,
  Filter,
  RefreshCw,
  Clock,
  Layers,
} from "lucide-react";

export default function VerificationStagePage() {
  const params = useParams();
  const router = useRouter();

  const documentId = (params?.documentId as string) || "";
  const stageSlug = (params?.stage as string) || "extract";

  // Polling hook: queries GET /api/documents/{id}/status every 2s while active
  const {
    data: statusData,
    isLoading: statusLoading,
    error: statusError,
    refetch: refetchStatus,
  } = useDocumentStatus(documentId);

  // Claims hook: queries GET /api/documents/{id}/claims
  const {
    data: claimsData,
    isLoading: claimsLoading,
    refetch: refetchClaims,
  } = useDocumentClaims(documentId, {}, Boolean(documentId));

  // Report hook: queries GET /api/documents/{id}/report
  const { data: reportData } = useDocumentReport(
    documentId,
    statusData?.status === "COMPLETED" || statusData?.pipeline_stage === "DONE"
  );

  // Local UI filters and selection state
  const [claimSearch, setClaimSearch] = useState("");
  const [verdictFilter, setVerdictFilter] = useState<string>("ALL");
  const [selectedClaimIndex, setSelectedClaimIndex] = useState<number>(0);
  const [reviewingClaim, setReviewingClaim] = useState<Claim | null>(null);

  const backendStage: PipelineStage = statusData?.pipeline_stage || "UPLOADED";
  const claims = claimsData?.items || reportData?.claims || [];

  // Filtered claims based on search and verdict filter
  const filteredClaims = claims.filter((c) => {
    const matchesSearch =
      !claimSearch.trim() ||
      c.claim_text.toLowerCase().includes(claimSearch.toLowerCase()) ||
      c.citations?.some((cit) => cit.reference_text?.toLowerCase().includes(claimSearch.toLowerCase()));

    const matchesVerdict =
      verdictFilter === "ALL" ||
      (verdictFilter === "NULL" && c.verdict === null) ||
      c.verdict === verdictFilter;

    return matchesSearch && matchesVerdict;
  });

  const selectedClaim = claims[selectedClaimIndex] || claims[0];

  return (
    <AppShell>
      <div className="space-y-6 pb-16">
        {/* Progress Tracker at top */}
        <ProgressTracker
          documentId={documentId}
          currentStageSlug={stageSlug}
          backendStage={backendStage}
        />

        {/* Polling / Processing Banner if still running */}
        {statusData?.status === "PROCESSING" && (
          <div className="p-4 rounded-[14px] bg-[#FFF0D6] dark:bg-[#33291F] border border-[#F4B860] flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 text-[#3E2F27] dark:text-[#F3E9DD]">
              <Spinner size="sm" />
              <span>
                Backend Pipeline Active: <strong>{statusData.pipeline_stage}</strong> ({statusData.progress_percent}%)
              </span>
            </div>
            <div className="flex items-center gap-3 text-[11px] font-mono text-[#7A685D] dark:text-[#B8A898]">
              <span>Found: {statusData.total_claims_found} claims</span>
              <span>•</span>
              <span>Verified: {statusData.verified_claims_count}</span>
            </div>
          </div>
        )}

        {/* STAGE 01: UPLOAD SUMMARY */}
        {stageSlug === "upload" && (
          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                Document Uploaded & Accepted
              </h3>
              <span className="font-mono text-xs bg-[#E4F1EA] text-[#1F5A42] px-2.5 py-1 rounded-full font-bold">
                201 ACCEPTED
              </span>
            </div>
            <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
              Document ID: <code className="font-mono">{documentId}</code>
            </p>
            <div className="pt-4">
              <Link href={`/verify/${documentId}/extract`}>
                <Button variant="primary" size="compact" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  Continue to Extraction
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* STAGE 02: CLAIM & CITATION EXTRACTION */}
        {stageSlug === "extract" && (
          <div className="space-y-6">
            {/* Stage counters */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
                <span className="text-[11px] font-bold uppercase text-[#7A685D] dark:text-[#B8A898]">Claims Extracted</span>
                <p className="text-2xl font-extrabold text-[#3E2F27] dark:text-[#F3E9DD] tabular-nums mt-1">
                  {claims.length}
                </p>
              </div>
              <div className="p-4 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
                <span className="text-[11px] font-bold uppercase text-[#7A685D] dark:text-[#B8A898]">Citations Detected</span>
                <p className="text-2xl font-extrabold text-[#3E2F27] dark:text-[#F3E9DD] tabular-nums mt-1">
                  {claims.reduce((acc, c) => acc + (c.citations?.length || 0), 0)}
                </p>
              </div>
              <div className="p-4 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
                <span className="text-[11px] font-bold uppercase text-[#7A685D] dark:text-[#B8A898]">References Parsed</span>
                <p className="text-2xl font-extrabold text-[#3E2F27] dark:text-[#F3E9DD] tabular-nums mt-1">
                  {claims.reduce((acc, c) => acc + (c.citations?.length || 0), 0)}
                </p>
              </div>
              <div className="p-4 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
                <span className="text-[11px] font-bold uppercase text-[#7A685D] dark:text-[#B8A898]">Warnings</span>
                <p className="text-2xl font-extrabold text-amber-700 dark:text-amber-400 tabular-nums mt-1">
                  0
                </p>
              </div>
            </div>

            {/* Extracted claims list */}
            <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-[#F0E4D2] dark:border-[#3D322A]">
                <div>
                  <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                    Extracted Scientific Claims ({claims.length})
                  </h3>
                  <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                    Factual statements parsed from the academic manuscript
                  </p>
                </div>
                <div className="w-full sm:w-64">
                  <SearchInput
                    value={claimSearch}
                    onChange={setClaimSearch}
                    placeholder="Search extracted claims..."
                  />
                </div>
              </div>

              {claimsLoading ? (
                <div className="space-y-3 py-6">
                  <Skeleton className="h-20 w-full" />
                  <Skeleton className="h-20 w-full" />
                </div>
              ) : filteredClaims.length > 0 ? (
                <div className="space-y-4">
                  {filteredClaims.map((claim, idx) => (
                    <div
                      key={claim.id || idx}
                      className="p-4 rounded-[12px] bg-[#FFF8E8]/50 dark:bg-[#1E1814]/50 border border-[#F0E4D2] dark:border-[#3D322A] space-y-3"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-[#8D6E63] dark:text-[#D7B8A8] font-mono">
                          Claim #{idx + 1} • Page {claim.page_number}
                        </span>
                        <div className="flex items-center gap-2">
                          <button
                            disabled
                            title="Editing extracted claims is not supported by the API yet."
                            className="text-[11px] text-[#A08B78] dark:text-[#8C7A6A] cursor-not-allowed hover:underline"
                          >
                            Edit Claim (Disabled)
                          </button>
                        </div>
                      </div>
                      <p className="text-xs sm:text-sm font-medium text-[#3E2F27] dark:text-[#F3E9DD] leading-relaxed">
                        &ldquo;{claim.claim_text}&rdquo;
                      </p>
                      {claim.citations && claim.citations.length > 0 && (
                        <div className="pt-2 border-t border-[#F0E4D2]/60 dark:border-[#3D322A]/60 flex flex-wrap gap-2 items-center text-xs">
                          <span className="text-[#7A685D] dark:text-[#B8A898] text-[11px] font-semibold">
                            Citations:
                          </span>
                          {claim.citations.map((c) => (
                            <span
                              key={c.id}
                              className="font-mono text-[11px] bg-white dark:bg-[#2A221C] px-2 py-0.5 rounded border border-[#F0E4D2] dark:border-[#3D322A] text-[#3E2F27] dark:text-[#F3E9DD]"
                            >
                              {c.raw_marker} {c.reference_text ? `— ${c.reference_text.slice(0, 40)}...` : ""}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center py-8 text-xs text-[#7A685D] dark:text-[#B8A898] italic">
                  No claims match the search filter.
                </p>
              )}

              <div className="flex justify-end pt-4 border-t border-[#F0E4D2] dark:border-[#3D322A]">
                <Link href={`/verify/${documentId}/map`}>
                  <Button variant="primary" size="compact" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                    Proceed to Citation Mapping
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* STAGE 03: CITATION MAPPING */}
        {stageSlug === "map" && (
          <div className="space-y-6">
            <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-4">
              <div>
                <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                  Citation Graph Mapping
                </h3>
                <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                  Visualizing relationship: CLAIM → CITATION MARKER → ORIGINAL BIBLIOGRAPHY REFERENCE
                </p>
              </div>

              {/* Claims to citations mapping list */}
              <div className="space-y-4">
                {claims.map((claim, idx) => (
                  <div
                    key={claim.id || idx}
                    className="p-5 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-sm space-y-3"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-[#8D6E63] dark:text-[#D7B8A8] font-mono">
                        Claim #{idx + 1} (Page {claim.page_number})
                      </span>
                      <button
                        disabled
                        title="Manual citation rematching is not supported by the API yet."
                        className="text-[11px] text-[#A08B78] dark:text-[#8C7A6A] cursor-not-allowed"
                      >
                        Rematch Citation (Disabled)
                      </button>
                    </div>

                    <p className="text-xs sm:text-sm font-medium text-[#3E2F27] dark:text-[#F3E9DD]">
                      &ldquo;{claim.claim_text}&rdquo;
                    </p>

                    {/* Mapping chain representation */}
                    <div className="mt-3 p-3 rounded-[10px] bg-[#FFF0D6]/30 dark:bg-[#33291F]/30 border border-[#F0E4D2] dark:border-[#3D322A] space-y-2">
                      {claim.citations && claim.citations.length > 0 ? (
                        claim.citations.map((c) => (
                          <div
                            key={c.id}
                            className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                          >
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-[#8D6E63] dark:text-[#D7B8A8] bg-white dark:bg-[#2A221C] px-2 py-0.5 rounded border border-[#F0E4D2] dark:border-[#3D322A]">
                                {c.raw_marker}
                              </span>
                              <span className="text-[#A08B78]">→</span>
                              <span className="text-[#3E2F27] dark:text-[#F3E9DD] truncate max-w-md">
                                {c.reference_text || "Referenced publication metadata"}
                              </span>
                            </div>
                            <CitationBadge status="MATCHED" size="sm" />
                          </div>
                        ))
                      ) : (
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-[#7A685D] dark:text-[#B8A898] italic">
                            No citation markers linked to this statement.
                          </span>
                          <CitationBadge status="MISSING_REFERENCE" size="sm" />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-[#F0E4D2] dark:border-[#3D322A]">
                <Link href={`/verify/${documentId}/extract`}>
                  <Button variant="outline" size="compact" leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}>
                    Back to Extraction
                  </Button>
                </Link>
                <Link href={`/verify/${documentId}/retrieve`}>
                  <Button variant="primary" size="compact" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                    Proceed to Research Retrieval
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* STAGE 04: ORIGINAL RESEARCH RETRIEVAL */}
        {stageSlug === "retrieve" && (
          <div className="space-y-6">
            <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div>
                  <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                    Retrieved Scholarly Publications
                  </h3>
                  <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                    Publications resolved through Crossref, OpenAlex, and Europe PMC
                  </p>
                </div>
                <div className="text-xs text-[#A08B78] dark:text-[#8C7A6A] italic">
                  Ad-hoc scholarly search is disabled (automated pipeline mode)
                </div>
              </div>

              {/* Research publications cards */}
              <div className="space-y-4">
                {claims.flatMap((c) => c.evidence || []).map((ev, idx) => (
                  <div
                    key={ev.id || idx}
                    className="p-5 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-sm space-y-3"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="text-xs font-bold text-[#8D6E63] dark:text-[#D7B8A8] font-mono uppercase">
                        Provider: {ev.source_provider}
                      </span>
                      <div className="flex items-center gap-2">
                        <EvidenceLevelBadge level={ev.evidence_level} />
                        <RetrievalBadge status={ev.retrieval_status} />
                      </div>
                    </div>

                    <div className="p-3 bg-[#FFF8E8] dark:bg-[#1E1814] rounded-[8px] border border-[#F0E4D2] dark:border-[#3D322A]">
                      <p className="text-xs text-[#3E2F27] dark:text-[#F3E9DD] leading-relaxed italic">
                        &ldquo;{ev.passage}&rdquo;
                      </p>
                    </div>

                    <div className="flex items-center justify-between text-xs text-[#7A685D] dark:text-[#B8A898]">
                      <span>Section: {ev.section_name || "Abstract / Main Body"}</span>
                      {ev.doi && (
                        <a
                          href={`https://doi.org/${ev.doi}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-mono text-[#8D6E63] hover:underline flex items-center gap-1"
                        >
                          doi:{ev.doi} <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
                ))}

                {claims.flatMap((c) => c.evidence || []).length === 0 && (
                  <p className="text-center py-8 text-xs text-[#7A685D] dark:text-[#B8A898] italic">
                    Retrieval is currently processing in the background...
                  </p>
                )}
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-[#F0E4D2] dark:border-[#3D322A]">
                <Link href={`/verify/${documentId}/map`}>
                  <Button variant="outline" size="compact" leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}>
                    Back to Mapping
                  </Button>
                </Link>
                <Link href={`/verify/${documentId}/compare`}>
                  <Button variant="primary" size="compact" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                    Proceed to Evidence Comparison
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* STAGE 05: EVIDENCE COMPARISON WORKSPACE */}
        {stageSlug === "compare" && (
          <div className="space-y-6">
            {/* Claim selector ribbon */}
            <div className="flex items-center gap-2 overflow-x-auto pb-2">
              {claims.map((c, idx) => (
                <button
                  key={c.id || idx}
                  onClick={() => setSelectedClaimIndex(idx)}
                  className={`px-3 py-1.5 rounded-[10px] text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                    selectedClaimIndex === idx
                      ? "bg-[#F4B860] text-[#3E2F27] shadow-sm font-bold"
                      : "bg-white dark:bg-[#2A221C] text-[#7A685D] dark:text-[#B8A898] border border-[#F0E4D2] dark:border-[#3D322A] hover:bg-[#FFF0D6]"
                  }`}
                >
                  <span>Claim #{idx + 1}</span>
                  <VerdictBadge verdict={c.verdict} size="sm" />
                </button>
              ))}
            </div>

            {/* Two-panel evidence comparison */}
            {selectedClaim ? (
              <EvidencePanel
                claim={selectedClaim}
                claimIndex={selectedClaimIndex}
                onOpenReviewModal={() => setReviewingClaim(selectedClaim)}
              />
            ) : (
              <p className="text-center py-8 text-xs text-[#7A685D] dark:text-[#B8A898] italic">
                No claim selected.
              </p>
            )}

            <div className="flex items-center justify-between pt-4">
              <Link href={`/verify/${documentId}/retrieve`}>
                <Button variant="outline" size="compact" leftIcon={<ArrowLeft className="w-3.5 h-3.5" />}>
                  Back to Research Retrieval
                </Button>
              </Link>
              <Link href={`/verify/${documentId}/verify`}>
                <Button variant="primary" size="compact" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                  Proceed to Final Verdicts
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* STAGE 06: VERIFICATION RESULTS & AUDIT */}
        {stageSlug === "verify" && (
          <div className="space-y-6">
            {/* 7 verdict counters */}
            <div className="p-4 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
              <p className="text-xs font-bold uppercase tracking-wider text-[#7A685D] dark:text-[#B8A898] mb-3">
                Verdict Breakdown Filter (Click to filter claims):
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setVerdictFilter("ALL")}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                    verdictFilter === "ALL"
                      ? "bg-[#3E2F27] text-white dark:bg-[#F3E9DD] dark:text-[#1E1814]"
                      : "bg-[#FFF0D6] dark:bg-[#33291F] text-[#3E2F27] dark:text-[#F3E9DD]"
                  }`}
                >
                  All Claims ({claims.length})
                </button>
                <button
                  onClick={() => setVerdictFilter("SUPPORTED")}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                    verdictFilter === "SUPPORTED"
                      ? "ring-2 ring-[#39765B] bg-[#E4F1EA] text-[#1F5A42]"
                      : "bg-[#E4F1EA] text-[#1F5A42]"
                  }`}
                >
                  Supported ({claims.filter((c) => c.verdict === "SUPPORTED").length})
                </button>
                <button
                  onClick={() => setVerdictFilter("PARTLY_SUPPORTED")}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                    verdictFilter === "PARTLY_SUPPORTED"
                      ? "ring-2 ring-[#B68A42] bg-[#F7EBCF] text-[#7A5A14]"
                      : "bg-[#F7EBCF] text-[#7A5A14]"
                  }`}
                >
                  Partially Supported ({claims.filter((c) => c.verdict === "PARTLY_SUPPORTED").length})
                </button>
                <button
                  onClick={() => setVerdictFilter("UNSUPPORTED")}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                    verdictFilter === "UNSUPPORTED"
                      ? "ring-2 ring-[#B94D4D] bg-[#F6E1E1] text-[#8F2E2E]"
                      : "bg-[#F6E1E1] text-[#8F2E2E]"
                  }`}
                >
                  Unsupported ({claims.filter((c) => c.verdict === "UNSUPPORTED").length})
                </button>
                <button
                  onClick={() => setVerdictFilter("CONTRADICTORY")}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                    verdictFilter === "CONTRADICTORY"
                      ? "ring-2 ring-[#74518C] bg-[#EDE3F3] text-[#54346B]"
                      : "bg-[#EDE3F3] text-[#54346B]"
                  }`}
                >
                  Contradictory ({claims.filter((c) => c.verdict === "CONTRADICTORY").length})
                </button>
                <button
                  onClick={() => setVerdictFilter("POTENTIALLY_OUTDATED")}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                    verdictFilter === "POTENTIALLY_OUTDATED"
                      ? "ring-2 ring-[#B77B35] bg-[#F8E7D2] text-[#8A5214]"
                      : "bg-[#F8E7D2] text-[#8A5214]"
                  }`}
                >
                  Potentially Outdated ({claims.filter((c) => c.verdict === "POTENTIALLY_OUTDATED").length})
                </button>
                <button
                  onClick={() => setVerdictFilter("NULL")}
                  className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                    verdictFilter === "NULL"
                      ? "ring-2 ring-[#766F68] bg-[#ECE8E4] text-[#4F4943]"
                      : "bg-[#ECE8E4] text-[#4F4943]"
                  }`}
                >
                  Needs Human Review ({claims.filter((c) => c.verdict === null).length})
                </button>
              </div>
            </div>

            {/* List of Claim Result Cards */}
            <div className="space-y-4">
              {filteredClaims.map((claim, idx) => (
                <ClaimCard
                  key={claim.id || idx}
                  claim={claim}
                  claimIndex={idx}
                  onReview={() => setReviewingClaim(claim)}
                  onSelect={() => {
                    setSelectedClaimIndex(idx);
                    router.push(`/verify/${documentId}/compare`);
                  }}
                />
              ))}
            </div>

            {/* Link to Final Report */}
            <div className="p-6 rounded-[16px] bg-[#FFF0D6]/50 dark:bg-[#33291F]/50 border border-[#F4B860] flex flex-col sm:flex-row items-center justify-between gap-4">
              <div>
                <h4 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                  Verification Analysis Complete
                </h4>
                <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                  Synthesized verification report with reliability scores and downloadable evidence trail is ready.
                </p>
              </div>
              <Link href={`/reports/${documentId}`}>
                <Button variant="primary" size="standard" rightIcon={<ArrowRight className="w-4 h-4" />}>
                  View Full Verification Report
                </Button>
              </Link>
            </div>
          </div>
        )}

        {/* Human review modal */}
        {reviewingClaim && (
          <HumanReviewPanel
            claim={reviewingClaim}
            isOpen={Boolean(reviewingClaim)}
            onClose={() => setReviewingClaim(null)}
            documentId={documentId}
            onSuccess={() => {
              refetchClaims();
            }}
          />
        )}
      </div>
    </AppShell>
  );
}
