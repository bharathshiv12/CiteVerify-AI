/**
 * Client-side API Service for CiteVerify AI.
 * Communicates with FastAPI backend using types defined in types/index.ts.
 */

import {
  Document,
  DocumentStatusResponse,
  ClaimListResponse,
  Claim,
  VerificationReport,
} from "../types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";

export async function checkHealth(): Promise<{ status: string; service: string; version: string; timestamp: string }> {
  const res = await fetch(`${API_BASE_URL}/api/health`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Health check failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<Document> {
  if (USE_MOCKS) {
    const mock = await import("../../contracts/examples/synthetic_document.json");
    return mock.default as unknown as Document;
  }

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Upload failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function startAnalysis(documentId: string): Promise<{ document_id: string; status: string }> {
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    throw new Error(`Failed to start analysis: HTTP ${res.status}`);
  }
  return res.json();
}

export async function getDocumentStatus(documentId: string): Promise<DocumentStatusResponse> {
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/status`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch status: HTTP ${res.status}`);
  }
  return res.json();
}

export async function getDocumentClaims(documentId: string, page = 1, pageSize = 20): Promise<ClaimListResponse> {
  if (USE_MOCKS) {
    const mock = await import("../../contracts/examples/synthetic_claims.json");
    return mock.default as unknown as ClaimListResponse;
  }

  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/claims?page=${page}&page_size=${pageSize}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch claims: HTTP ${res.status}`);
  }
  return res.json();
}

export async function getDocumentReport(documentId: string): Promise<VerificationReport> {
  if (USE_MOCKS) {
    const mock = await import("../../contracts/examples/synthetic_report.json");
    return mock.default as unknown as VerificationReport;
  }

  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/report`);
  if (!res.ok) {
    throw new Error(`Failed to fetch report: HTTP ${res.status}`);
  }
  return res.json();
}

