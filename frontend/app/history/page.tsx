"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { AppShell } from "../../components/layout/app-shell";
import { Button } from "../../components/ui/button";
import { SearchInput } from "../../components/ui/search-input";
import { EmptyState } from "../../components/ui/empty-state";
import { ConfirmDialog } from "../../components/ui/confirm-dialog";
import { useAuth } from "../../lib/supabase/auth-context";
import {
  getRegisteredDocuments,
  unregisterDocument,
  RegisteredDocument,
} from "../../lib/document-registry";
import { getDocumentReport, getDocumentStatus, USE_MOCKS } from "../../services/api";
import { VerificationReport, DocumentStatusResponse } from "../../types";
import {
  History,
  Trash2,
  ExternalLink,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
} from "lucide-react";

export default function HistoryPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<RegisteredDocument[]>([]);
  const [reportsMap, setReportsMap] = useState<Record<string, VerificationReport>>({});
  const [statusMap, setStatusMap] = useState<Record<string, DocumentStatusResponse>>({});
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<"ALL" | "COMPLETED" | "PROCESSING" | "NEEDS_REVIEW">("ALL");

  const [documentToDelete, setDocumentToDelete] = useState<RegisteredDocument | null>(null);

  useEffect(() => {
    const docs = getRegisteredDocuments(user?.id);
    setDocuments(docs);

    if (docs.length === 0 && USE_MOCKS) {
      const mockDoc: RegisteredDocument = {
        document_id: "00000000-0000-0000-0000-000000000001",
        filename: "synthetic_sample_paper_v1.pdf",
        uploaded_at: new Date().toISOString(),
      };
      setDocuments([mockDoc]);
      getDocumentReport(mockDoc.document_id).then((rep) => {
        setReportsMap({ [mockDoc.document_id]: rep });
      });
      return;
    }

    docs.forEach(async (d) => {
      try {
        const status = await getDocumentStatus(d.document_id);
        setStatusMap((prev) => ({ ...prev, [d.document_id]: status }));
      } catch {}

      try {
        const report = await getDocumentReport(d.document_id);
        setReportsMap((prev) => ({ ...prev, [d.document_id]: report }));
      } catch {}
    });
  }, [user]);

  const handleConfirmRemove = () => {
    if (!documentToDelete) return;
    const updated = unregisterDocument(documentToDelete.document_id, user?.id);
    setDocuments(updated);
    setDocumentToDelete(null);
  };

  const filteredDocs = documents.filter((d) => {
    const matchesSearch = !search.trim() || d.filename.toLowerCase().includes(search.toLowerCase());
    const rep = reportsMap[d.document_id];
    const stat = statusMap[d.document_id];

    if (filter === "COMPLETED") {
      return matchesSearch && (stat?.status === "COMPLETED" || Boolean(rep));
    }
    if (filter === "PROCESSING") {
      return matchesSearch && stat?.status === "PROCESSING";
    }
    if (filter === "NEEDS_REVIEW") {
      return matchesSearch && (rep?.human_review_required_count || 0) > 0;
    }
    return matchesSearch;
  });

  return (
    <AppShell>
      <div className="space-y-6 pb-16">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
          <div>
            <h2 className="text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
              Device Verification History
            </h2>
            <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
              Research manuscripts uploaded and verified on this device
            </p>
          </div>
          <div className="w-full sm:w-64">
            <SearchInput value={search} onChange={setSearch} placeholder="Search history..." />
          </div>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {(["ALL", "COMPLETED", "PROCESSING", "NEEDS_REVIEW"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                filter === tab
                  ? "bg-[#3E2F27] text-white dark:bg-[#F3E9DD] dark:text-[#1E1814]"
                  : "bg-white dark:bg-[#2A221C] text-[#7A685D] dark:text-[#B8A898] border border-[#F0E4D2] dark:border-[#3D322A] hover:bg-[#FFF0D6]"
              }`}
            >
              {tab === "ALL" && `All Documents (${documents.length})`}
              {tab === "COMPLETED" && "Completed"}
              {tab === "PROCESSING" && "Processing"}
              {tab === "NEEDS_REVIEW" && "Needs Human Review"}
            </button>
          ))}
        </div>

        {/* Documents Table */}
        {filteredDocs.length > 0 ? (
          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#F0E4D2] dark:border-[#3D322A] text-[#7A685D] dark:text-[#B8A898]">
                    <th className="py-3 font-semibold">Document Name</th>
                    <th className="py-3 font-semibold">Upload Date</th>
                    <th className="py-3 font-semibold text-center">Claims</th>
                    <th className="py-3 font-semibold text-center">Status</th>
                    <th className="py-3 font-semibold text-center">Human Review</th>
                    <th className="py-3 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F0E4D2]/60 dark:divide-[#3D322A]/60">
                  {filteredDocs.map((d) => {
                    const rep = reportsMap[d.document_id];
                    const stat = statusMap[d.document_id];
                    const dateStr = new Date(d.uploaded_at).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    });

                    return (
                      <tr key={d.document_id} className="hover:bg-[#FFF0D6]/30 dark:hover:bg-[#33291F]/30">
                        <td className="py-3.5 font-medium text-[#3E2F27] dark:text-[#F3E9DD] max-w-xs truncate">
                          📄 {d.filename}
                        </td>
                        <td className="py-3.5 text-[#7A685D] dark:text-[#B8A898]">{dateStr}</td>
                        <td className="py-3.5 text-center font-mono tabular-nums">
                          {rep?.total_claims ?? stat?.total_claims_found ?? "—"}
                        </td>
                        <td className="py-3.5 text-center">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[11px] font-bold font-mono ${
                              stat?.status === "COMPLETED" || rep
                                ? "bg-[#E4F1EA] text-[#1F5A42]"
                                : stat?.status === "PROCESSING"
                                ? "bg-[#FFF0D6] text-[#8D6E63]"
                                : "bg-stone-200 text-stone-700 dark:bg-stone-800 dark:text-stone-300"
                            }`}
                          >
                            {stat?.status || (rep ? "COMPLETED" : "PENDING")}
                          </span>
                        </td>
                        <td className="py-3.5 text-center">
                          {(rep?.human_review_required_count || 0) > 0 ? (
                            <span className="text-[11px] text-amber-800 dark:text-amber-300 font-semibold bg-amber-100 dark:bg-amber-950/40 px-2 py-0.5 rounded-full">
                              {rep?.human_review_required_count} Flagged
                            </span>
                          ) : (
                            <span className="text-[#A08B78] text-[11px]">Clear</span>
                          )}
                        </td>
                        <td className="py-3.5 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Link href={`/verify/${d.document_id}/extract`}>
                              <Button variant="outline" size="compact">
                                Verify
                              </Button>
                            </Link>
                            <Link href={`/reports/${d.document_id}`}>
                              <Button variant="secondary" size="compact">
                                Report
                              </Button>
                            </Link>
                            <button
                              onClick={() => setDocumentToDelete(d)}
                              className="p-1.5 rounded-lg text-[#7A685D] hover:text-red-600 dark:hover:text-red-400 hover:bg-[#F6E1E1]/40 transition-colors"
                              title="Remove from device history"
                              aria-label="Remove document"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <EmptyState
            title="No documents in history"
            description="Your device verification history is empty. Documents you verify will appear here for audit review."
            actionLabel="Start a new verification"
            onAction={() => window.location.assign("/verify")}
          />
        )}

        {/* Device Removal Confirmation Dialog */}
        <ConfirmDialog
          isOpen={Boolean(documentToDelete)}
          onClose={() => setDocumentToDelete(null)}
          onConfirm={handleConfirmRemove}
          variant="danger"
          title="Remove from Device History?"
          message="This removes the document from your device's history. It does not delete the server copy."
          confirmLabel="Remove from Device"
        />
      </div>
    </AppShell>
  );
}
