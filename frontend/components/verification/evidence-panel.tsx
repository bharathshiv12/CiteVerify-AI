import React from "react";
import { Claim } from "../../types";
import { VerdictBadge, EvidenceLevelBadge, RetrievalBadge } from "../ui/status-badge";
import { ConfidenceIndicator } from "./confidence-indicator";
import { ExternalLink, UserCheck, BookOpen, FileText, AlertCircle } from "lucide-react";
import { Button } from "../ui/button";

interface EvidencePanelProps {
  claim: Claim;
  claimIndex: number;
  onOpenReviewModal?: () => void;
}

export function EvidencePanel({
  claim,
  claimIndex,
  onOpenReviewModal,
}: EvidencePanelProps) {
  const hasEvidence = claim.evidence && claim.evidence.length > 0;

  return (
    <div className="w-full bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] rounded-[14px] shadow-brand overflow-hidden">
      {/* Header bar */}
      <div className="p-4 sm:p-5 bg-[#FFF0D6]/40 dark:bg-[#33291F]/40 border-b border-[#F0E4D2] dark:border-[#3D322A] flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 rounded-full bg-[#F4B860] text-[#3E2F27] text-sm font-bold flex items-center justify-center font-mono">
            #{claimIndex + 1}
          </span>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
              Evidence Comparison Analysis
            </h3>
            <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
              Comparing extracted claim statement against retrieved scholarly publication passages
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <VerdictBadge verdict={claim.verdict} />
          <ConfidenceIndicator confidence={claim.confidence} showBar={false} />
          {onOpenReviewModal && (
            <Button
              variant="outline"
              size="compact"
              onClick={onOpenReviewModal}
              leftIcon={<UserCheck className="w-3.5 h-3.5" />}
            >
              Review Verdict
            </Button>
          )}
        </div>
      </div>

      {/* Two-panel comparison grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-[#F0E4D2] dark:divide-[#3D322A]">
        {/* LEFT PANEL: Original Scientific Claim */}
        <div className="p-5 sm:p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[#8D6E63] dark:text-[#D7B8A8] flex items-center gap-1.5">
              <FileText className="w-4 h-4" />
              Original Claim in Document
            </span>
            <span className="text-xs font-mono bg-[#FFF0D6] dark:bg-[#33291F] px-2 py-0.5 rounded text-[#7A685D] dark:text-[#B8A898]">
              Page {claim.page_number}
            </span>
          </div>

          <blockquote className="p-4 rounded-[10px] bg-[#FFF8E8] dark:bg-[#1E1814] border-l-4 border-[#F4B860] text-sm sm:text-base font-medium text-[#3E2F27] dark:text-[#F3E9DD] leading-relaxed italic">
            &ldquo;{claim.claim_text}&rdquo;
          </blockquote>

          {/* Attached Citations */}
          <div>
            <h4 className="text-xs font-semibold text-[#7A685D] dark:text-[#B8A898] uppercase tracking-wider mb-2">
              Attached Citation Markers:
            </h4>
            <div className="space-y-2">
              {claim.citations && claim.citations.length > 0 ? (
                claim.citations.map((cit, idx) => (
                  <div
                    key={cit.id || idx}
                    className="p-3 rounded-[10px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] text-xs"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-[#8D6E63] dark:text-[#D7B8A8]">
                        {cit.raw_marker} ({cit.marker_type})
                      </span>
                      <span className="text-[11px] text-[#7A685D] dark:text-[#B8A898]">
                        Ref #{cit.reference_index ?? idx + 1}
                      </span>
                    </div>
                    {cit.reference_text ? (
                      <p className="text-[#3E2F27] dark:text-[#F3E9DD] text-[11px] leading-relaxed">
                        {cit.reference_text}
                      </p>
                    ) : (
                      <p className="text-[#7A685D] dark:text-[#B8A898] italic text-[11px]">
                        Bibliography reference text pending extraction
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-xs text-[#7A685D] dark:text-[#B8A898] italic">
                  No citation markers attached to this claim.
                </p>
              )}
            </div>
          </div>

          {/* Verification Engine Rationale */}
          {claim.rationale && (
            <div className="p-3.5 rounded-[10px] bg-[#FFF0D6]/40 dark:bg-[#33291F]/40 border border-[#F0E4D2] dark:border-[#3D322A]">
              <span className="text-xs font-semibold text-[#8D6E63] dark:text-[#D7B8A8] block mb-1">
                Verification Engine Rationale:
              </span>
              <p className="text-xs text-[#3E2F27] dark:text-[#F3E9DD] leading-relaxed">
                {claim.rationale}
              </p>
            </div>
          )}

          {/* Honesty note on structured indicators */}
          <div className="text-[11px] text-[#A08B78] dark:text-[#8C7A6A] flex items-start gap-1.5 pt-1">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
            <span>
              Detailed comparison breakdown indicators (methodology, sample size, effect size) are not provided by the verification engine yet.
            </span>
          </div>
        </div>

        {/* RIGHT PANEL: Retrieved Source Evidence */}
        <div className="p-5 sm:p-6 space-y-4 bg-white/50 dark:bg-[#2A221C]/50">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-[#8D6E63] dark:text-[#D7B8A8] flex items-center gap-1.5">
              <BookOpen className="w-4 h-4" />
              Retrieved Source Evidence
            </span>
            <span className="text-xs text-[#7A685D] dark:text-[#B8A898]">
              {claim.evidence?.length || 0} Passages Found
            </span>
          </div>

          {hasEvidence ? (
            <div className="space-y-4">
              {claim.evidence.map((ev, idx) => (
                <div
                  key={ev.id || idx}
                  className="p-4 rounded-[10px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-sm space-y-3"
                >
                  {/* Top metadata tags */}
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[#F0E4D2]/60 dark:border-[#3D322A]/60">
                    <div className="flex items-center gap-1.5">
                      <EvidenceLevelBadge level={ev.evidence_level} />
                      <RetrievalBadge status={ev.retrieval_status} />
                    </div>
                    <span className="text-[11px] font-mono text-[#7A685D] dark:text-[#B8A898] uppercase">
                      Provider: {ev.source_provider}
                    </span>
                  </div>

                  {/* Section name if available */}
                  {ev.section_name && (
                    <div className="text-xs font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">
                      Section: {ev.section_name}
                    </div>
                  )}

                  {/* Exact Retrieved Evidence Passage */}
                  <div className="p-3 bg-[#FFF8E8]/70 dark:bg-[#1E1814]/70 rounded-[8px] border border-[#F0E4D2] dark:border-[#3D322A]">
                    <p className="text-xs text-[#3E2F27] dark:text-[#F3E9DD] leading-relaxed">
                      &ldquo;{ev.passage}&rdquo;
                    </p>
                  </div>

                  {/* Similarity score & Source link */}
                  <div className="flex items-center justify-between pt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
                    {ev.similarity_score !== undefined && ev.similarity_score !== null && (
                      <span className="text-[11px]">
                        Semantic Match:{" "}
                        <strong className="text-[#3E2F27] dark:text-[#F3E9DD]">
                          {Math.round(ev.similarity_score * 100)}%
                        </strong>
                      </span>
                    )}

                    {ev.doi ? (
                      <a
                        href={`https://doi.org/${ev.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] text-[#8D6E63] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD] font-mono font-medium underline"
                      >
                        doi:{ev.doi}
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : ev.url ? (
                      <a
                        href={ev.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-[11px] text-[#8D6E63] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD] font-medium underline"
                      >
                        View Paper
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 rounded-[10px] bg-[#FFF0D6]/30 dark:bg-[#33291F]/30 border border-dashed border-[#A08B78]/40 text-center space-y-2">
              <AlertCircle className="w-6 h-6 text-[#7A685D] mx-auto" />
              <h4 className="text-sm font-semibold text-[#3E2F27] dark:text-[#F3E9DD]">
                No evidence passage could be retrieved for this citation.
              </h4>
              <p className="text-xs text-[#7A685D] dark:text-[#B8A898] max-w-sm mx-auto leading-relaxed">
                The cited paper was either paywalled, not indexed in open scholarly APIs, or lacked extractable open-access text. Retrieval failure does not imply the scientific claim is false.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
