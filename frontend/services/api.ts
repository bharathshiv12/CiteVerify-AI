/**
 * CiteVerify AI — Canonical API Client
 * Connects the frontend to FastAPI backend endpoints adhering strictly to OpenAPI 3.1.0 specifications.
 */

import {
  Document,
  DocumentStatusResponse,
  DocumentAnalyzeResponse,
  ClaimListResponse,
  Claim,
  VerificationReport,
  ClaimReviewRequest,
  ErrorEnvelope,
  VerificationVerdict,
  PaginatedDocuments,
  DashboardStats,
} from "../types";
import { getSupabaseClient } from "../lib/supabase/client";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ||
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
  "http://localhost:8000";

export const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS === "true";

export class ApiError extends Error {
  code: string;
  details?: Record<string, unknown>;
  request_id?: string;
  status: number;

  constructor(message: string, status: number, code = "UNKNOWN_ERROR", details?: Record<string, unknown>, request_id?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
    this.request_id = request_id;
  }
}

async function getAuthHeader(): Promise<Record<string, string>> {
  const supabase = getSupabaseClient();
  if (supabase) {
    try {
      const { data } = await supabase.auth.getSession();
      if (data.session?.access_token) {
        return { Authorization: `Bearer ${data.session.access_token}` };
      }
    } catch {
      // Supabase not reachable or anonymous
    }
  }
  return {};
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorEnvelope: ErrorEnvelope | null = null;
    try {
      errorEnvelope = await res.json();
    } catch {
      // Not JSON
    }

    const code = errorEnvelope?.error?.code || `HTTP_${res.status}`;
    const message = errorEnvelope?.error?.message || `Request failed with status ${res.status}`;
    const details = errorEnvelope?.error?.details;
    const request_id = errorEnvelope?.error?.request_id;

    if (res.status === 401 && typeof window !== "undefined") {
      const isAuthPage =
        window.location.pathname.startsWith("/login") ||
        window.location.pathname.startsWith("/signup") ||
        window.location.pathname.startsWith("/auth");
      if (!isAuthPage) {
        const supabase = getSupabaseClient();
        if (supabase) {
          supabase.auth.getSession().then(({ data }) => {
            if (!data.session) {
              window.location.href = "/login?expired=true";
            }
          });
        }
      }
    }

    throw new ApiError(message, res.status, code, details, request_id);
  }
  return res.json() as Promise<T>;
}

export async function checkHealth(): Promise<{ status: string; service: string; version: string; timestamp: string }> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/health`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    return handleResponse(res);
  } catch (err: unknown) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      err instanceof Error ? err.message : "Network error contacting backend",
      0,
      "NETWORK_ERROR"
    );
  }
}

export async function uploadDocument(file: File): Promise<Document> {
  if (USE_MOCKS) {
    const mock = await import("../lib/fixtures/synthetic_document.json");
    const synthetic = {
      ...(mock.default as unknown as Document),
      id: "00000000-0000-0000-0000-000000000001",
      filename: file.name,
      file_size_bytes: file.size,
      status: "PENDING" as const,
      pipeline_stage: "UPLOADED" as const,
    };
    return synthetic;
  }

  const authHeader = await getAuthHeader();
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    headers: {
      ...authHeader,
    },
    body: formData,
  });

  return handleResponse<Document>(res);
}

export async function startAnalysis(documentId: string): Promise<DocumentAnalyzeResponse> {
  if (USE_MOCKS) {
    return {
      document_id: documentId,
      status: "PROCESSING",
      pipeline_stage: "TEXT_EXTRACTION",
      message: "Document analysis pipeline started in mock mode.",
    };
  }

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeader,
    },
  });

  return handleResponse<DocumentAnalyzeResponse>(res);
}

export async function getDocumentStatus(documentId: string): Promise<DocumentStatusResponse> {
  if (USE_MOCKS) {
    return {
      document_id: documentId,
      status: "COMPLETED",
      pipeline_stage: "DONE",
      progress_percent: 100,
      total_claims_found: 2,
      verified_claims_count: 2,
      error_message: null,
    };
  }

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/status`, {
    headers: {
      Accept: "application/json",
      ...authHeader,
    },
    cache: "no-store",
  });

  return handleResponse<DocumentStatusResponse>(res);
}

export interface GetClaimsParams {
  verdict?: VerificationVerdict;
  needs_review?: boolean;
  page?: number;
  page_size?: number;
}

export async function getDocumentClaims(
  documentId: string,
  params: GetClaimsParams = {}
): Promise<ClaimListResponse> {
  if (USE_MOCKS) {
    const mock = await import("../lib/fixtures/synthetic_claims.json");
    let items = (mock.default as unknown as ClaimListResponse).items;
    if (params.verdict) {
      items = items.filter((c) => c.verdict === params.verdict);
    }
    if (typeof params.needs_review === "boolean") {
      items = items.filter((c) => c.needs_human_review === params.needs_review);
    }
    return {
      items,
      page: params.page || 1,
      page_size: params.page_size || 20,
      total: items.length,
    };
  }

  const authHeader = await getAuthHeader();
  const query = new URLSearchParams();
  if (params.verdict) query.set("verdict", params.verdict);
  if (typeof params.needs_review === "boolean") query.set("needs_review", String(params.needs_review));
  if (params.page) query.set("page", String(params.page));
  if (params.page_size) query.set("page_size", String(params.page_size));

  const qs = query.toString();
  const url = `${API_BASE_URL}/api/documents/${documentId}/claims${qs ? `?${qs}` : ""}`;

  const res = await fetch(url, {
    headers: {
      Accept: "application/json",
      ...authHeader,
    },
    cache: "no-store",
  });

  return handleResponse<ClaimListResponse>(res);
}

export async function getDocumentReport(documentId: string): Promise<VerificationReport> {
  if (USE_MOCKS) {
    const mock = await import("../lib/fixtures/synthetic_report.json");
    return mock.default as unknown as VerificationReport;
  }

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/report`, {
    headers: {
      Accept: "application/json",
      ...authHeader,
    },
    cache: "no-store",
  });

  return handleResponse<VerificationReport>(res);
}

export async function getClaimDetails(claimId: string): Promise<Claim> {
  if (USE_MOCKS) {
    const mock = await import("../lib/fixtures/synthetic_claims.json");
    const items = (mock.default as unknown as ClaimListResponse).items;
    const found = items.find((c) => c.id === claimId);
    if (!found) {
      throw new ApiError("Claim not found in synthetic fixtures", 404, "NOT_FOUND");
    }
    return found;
  }

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/claims/${claimId}`, {
    headers: {
      Accept: "application/json",
      ...authHeader,
    },
    cache: "no-store",
  });

  return handleResponse<Claim>(res);
}

export async function submitClaimReview(
  claimId: string,
  review: ClaimReviewRequest
): Promise<Claim> {
  if (USE_MOCKS) {
    const mock = await import("../lib/fixtures/synthetic_claims.json");
    const items = (mock.default as unknown as ClaimListResponse).items;
    const found = items.find((c) => c.id === claimId) || items[0];
    return {
      ...found,
      verdict: review.updated_verdict,
      needs_human_review: false,
      rationale: `Human reviewer (${review.reviewer_name}) updated verdict: ${review.notes}`,
    };
  }

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/claims/${claimId}/review`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...authHeader,
    },
    body: JSON.stringify(review),
  });

  return handleResponse<Claim>(res);
}

export async function listDocuments(page = 1, pageSize = 50): Promise<PaginatedDocuments> {
  if (USE_MOCKS) {
    return {
      items: [],
      page: 1,
      page_size: pageSize,
      total: 0,
    };
  }

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/documents?page=${page}&page_size=${pageSize}`, {
    headers: {
      Accept: "application/json",
      ...authHeader,
    },
    cache: "no-store",
  });

  return handleResponse<PaginatedDocuments>(res);
}

export async function deleteDocument(documentId: string): Promise<void> {
  if (USE_MOCKS) return;

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
    method: "DELETE",
    headers: {
      ...authHeader,
    },
  });

  if (!res.ok && res.status !== 204) {
    throw new ApiError("Failed to delete document", res.status, "DELETE_ERROR");
  }
}

export async function downloadReportPdf(documentId: string): Promise<Blob> {
  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/documents/${documentId}/report/pdf`, {
    headers: {
      ...authHeader,
    },
  });

  if (!res.ok) {
    throw new ApiError("Failed to download PDF report", res.status, "DOWNLOAD_ERROR");
  }

  return res.blob();
}

export async function getDashboardStats(): Promise<DashboardStats> {
  if (USE_MOCKS) {
    return {
      total_documents: 1,
      total_claims: 2,
      supported_claims: 1,
      partly_supported_claims: 0,
      unsupported_claims: 0,
      contradictory_claims: 0,
      outdated_claims: 0,
      needs_review_claims: 1,
      average_reliability_score: 75.0,
    };
  }

  const authHeader = await getAuthHeader();
  const res = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
    headers: {
      Accept: "application/json",
      ...authHeader,
    },
    cache: "no-store",
  });

  return handleResponse<DashboardStats>(res);
}
