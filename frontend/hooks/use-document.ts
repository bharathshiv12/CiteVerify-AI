"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getDocumentStatus,
  getDocumentReport,
  getDocumentClaims,
  startAnalysis,
  uploadDocument,
  GetClaimsParams,
} from "../services/api";
import { DocumentStatusResponse, VerificationReport, ClaimListResponse } from "../types";

export function useDocumentStatus(documentId: string, enabled = true) {
  return useQuery<DocumentStatusResponse>({
    queryKey: ["document-status", documentId],
    queryFn: () => getDocumentStatus(documentId),
    enabled: Boolean(documentId) && enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "PROCESSING" || status === "PENDING") {
        return 2000; // Poll every 2 seconds while active
      }
      return false; // Stop when completed or failed
    },
    refetchOnWindowFocus: true,
  });
}

export function useDocumentReport(documentId: string, enabled = true) {
  return useQuery<VerificationReport>({
    queryKey: ["document-report", documentId],
    queryFn: () => getDocumentReport(documentId),
    enabled: Boolean(documentId) && enabled,
    retry: 1,
  });
}

export function useDocumentClaims(documentId: string, params: GetClaimsParams = {}, enabled = true) {
  return useQuery<ClaimListResponse>({
    queryKey: ["document-claims", documentId, params],
    queryFn: () => getDocumentClaims(documentId, params),
    enabled: Boolean(documentId) && enabled,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["document-status", data.id] });
    },
  });
}

export function useStartAnalysis() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (documentId: string) => startAnalysis(documentId),
    onSuccess: (_, documentId) => {
      queryClient.invalidateQueries({ queryKey: ["document-status", documentId] });
    },
  });
}
