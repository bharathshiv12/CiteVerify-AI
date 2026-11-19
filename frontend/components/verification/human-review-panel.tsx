"use client";

import React, { useState } from "react";
import { Modal } from "../ui/modal";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Textarea } from "../ui/textarea";
import { Select } from "../ui/select";
import { Claim, VerificationVerdict } from "../../types";
import { useSubmitClaimReview } from "../../hooks/use-claim";
import { useAuth } from "../../lib/supabase/auth-context";
import { VERDICT_CONFIGS } from "../../lib/constants/verdicts";

interface HumanReviewPanelProps {
  claim: Claim | null;
  isOpen: boolean;
  onClose: () => void;
  documentId?: string;
  onSuccess?: (updatedClaim: Claim) => void;
}

export function HumanReviewPanel({
  claim,
  isOpen,
  onClose,
  documentId,
  onSuccess,
}: HumanReviewPanelProps) {
  const { fullName } = useAuth();
  const [reviewerName, setReviewerName] = useState(fullName || "");
  const [verdict, setVerdict] = useState<VerificationVerdict>(
    claim?.verdict || "SUPPORTED"
  );
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);

  const reviewMutation = useSubmitClaimReview(documentId);

  if (!claim) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewerName.trim()) {
      setError("Reviewer name is required.");
      return;
    }
    if (!notes.trim()) {
      setError("Reviewer rationale / notes are required.");
      return;
    }

    setError(null);
    try {
      const updated = await reviewMutation.mutateAsync({
        claimId: claim.id,
        review: {
          reviewer_name: reviewerName.trim(),
          updated_verdict: verdict,
          notes: notes.trim(),
        },
      });
      onSuccess?.(updated);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to submit review.");
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Submit Expert Human Review"
      description="Record human audit verdict, explanation, and notes according to academic verification standards."
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Claim context summary */}
        <div className="p-3 rounded-[10px] bg-[#FFF0D6]/40 dark:bg-[#33291F]/40 border border-[#F0E4D2] dark:border-[#3D322A] text-xs">
          <span className="font-semibold text-[#8D6E63] dark:text-[#D7B8A8] block mb-1">
            Claim Statement:
          </span>
          <p className="text-[#3E2F27] dark:text-[#F3E9DD] italic leading-relaxed">
            &ldquo;{claim.claim_text}&rdquo;
          </p>
        </div>

        <Input
          label="Reviewer Name or Institutional Identifier"
          required
          value={reviewerName}
          onChange={(e) => setReviewerName(e.target.value)}
          placeholder="e.g. Dr. A. Sharma or Reviewer #2"
        />

        <Select
          label="Verified Verdict"
          required
          value={verdict}
          onChange={(e) => setVerdict(e.target.value as VerificationVerdict)}
        >
          {Object.entries(VERDICT_CONFIGS).map(([val, conf]) => (
            <option key={val} value={val}>
              {conf.label}
            </option>
          ))}
        </Select>

        <Textarea
          label="Reviewer Notes / Evidence Rationale"
          required
          rows={3}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Document the exact findings, section tables, or reason for this verdict..."
        />

        {error && (
          <p className="text-xs text-red-600 dark:text-red-400 font-medium">
            {error}
          </p>
        )}

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#F0E4D2] dark:border-[#3D322A]">
          <Button
            type="button"
            variant="outline"
            size="compact"
            onClick={onClose}
            disabled={reviewMutation.isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            size="compact"
            isLoading={reviewMutation.isPending}
          >
            Submit Audit Decision
          </Button>
        </div>
      </form>
    </Modal>
  );
}
