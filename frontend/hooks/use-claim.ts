"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getClaimDetails, submitClaimReview } from "../services/api";
import { Claim, ClaimReviewRequest } from "../types";

export function useClaimDetails(claimId: string, enabled = true) {
  return useQuery<Claim>({
    queryKey: ["claim-details", claimId],
    queryFn: () => getClaimDetails(claimId),
    enabled: Boolean(claimId) && enabled,
  });
}

export function useSubmitClaimReview(documentId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ claimId, review }: { claimId: string; review: ClaimReviewRequest }) =>
      submitClaimReview(claimId, review),
    onSuccess: (updatedClaim) => {
      queryClient.setQueryData(["claim-details", updatedClaim.id], updatedClaim);
      if (documentId) {
        queryClient.invalidateQueries({ queryKey: ["document-claims", documentId] });
        queryClient.invalidateQueries({ queryKey: ["document-report", documentId] });
      }
    },
  });
}
