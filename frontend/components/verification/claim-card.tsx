import React from "react";
import { Claim } from "../../types";
import { VerdictBadge } from "../ui/status-badge";
import { ConfidenceIndicator } from "./confidence-indicator";
import { FileText, BookOpen, UserCheck, ChevronRight } from "lucide-react";
import { Button } from "../ui/button";

interface ClaimCardProps {
  claim: Claim;
  claimIndex: number;
  onSelect?: () => void;
  onReview?: () => void;
  isSelected?: boolean;
}

export function ClaimCard({
  claim,
  claimIndex,
  onSelect,
  onReview,
  isSelected = false,
}: ClaimCardProps) {
  const citationCount = claim.citations?.length || 0;
  const evidenceCount = claim.evidence?.length || 0;

  return (
    <div
      className={`p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border transition-all ${
        isSelected
          ? "border-[#F4B860] ring-2 ring-[#F4B860]/20 shadow-brand"
          : "border-[#F0E4D2] dark:border-[#3D322A] hover:border-[#A08B78] dark:hover:border-[#8C7A6A]"
      }`}
    >
      {/* Top Header: Claim number, Page, Verdict & Confidence */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3 pb-3 border-b border-[#F0E4D2]/60 dark:border-[#3D322A]/60">
        <div className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-full bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] text-xs font-bold flex items-center justify-center font-mono">
            #{claimIndex + 1}
          </span>
          <span className="text-xs font-semibold text-[#7A685D] dark:text-[#B8A898] flex items-center gap-1">
            <FileText className="w-3.5 h-3.5" />
            Page {claim.page_number}
          </span>
          {claim.needs_human_review && (
            <span className="text-[11px] font-semibold text-[#8A5214] bg-[#F8E7D2] dark:bg-[#B77B35]/20 dark:text-[#fdba74] px-2 py-0.5 rounded-full flex items-center gap-1 border border-[#B77B35]/20">
              <UserCheck className="w-3 h-3" />
              Needs Review
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <VerdictBadge verdict={claim.verdict} />
          <ConfidenceIndicator confidence={claim.confidence} showBar={false} />
        </div>
      </div>

      {/* Claim statement */}
      <div className="mb-4">
        <p className="text-sm font-medium text-[#3E2F27] dark:text-[#F3E9DD] leading-relaxed">
          &ldquo;{claim.claim_text}&rdquo;
        </p>
      </div>

      {/* Rationale if present */}
      {claim.rationale && (
        <div className="mb-4 p-3 rounded-[10px] bg-[#FFF0D6]/50 dark:bg-[#33291F]/50 border border-[#F0E4D2] dark:border-[#3D322A] text-xs text-[#7A685D] dark:text-[#B8A898]">
          <span className="font-semibold text-[#8D6E63] dark:text-[#D7B8A8] block mb-1">
            Verification Rationale:
          </span>
          <p>{claim.rationale}</p>
        </div>
      )}

      {/* Footer metadata and actions */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs text-[#7A685D] dark:text-[#B8A898]">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            <BookOpen className="w-3.5 h-3.5" />
            {citationCount} {citationCount === 1 ? "Citation" : "Citations"}
          </span>
          <span>•</span>
          <span>{evidenceCount} Evidence Passages</span>
        </div>

        <div className="flex items-center gap-2">
          {onReview && (
            <Button variant="outline" size="compact" onClick={onReview}>
              Review
            </Button>
          )}
          {onSelect && (
            <Button
              variant="secondary"
              size="compact"
              onClick={onSelect}
              rightIcon={<ChevronRight className="w-3.5 h-3.5" />}
            >
              Compare Evidence
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
