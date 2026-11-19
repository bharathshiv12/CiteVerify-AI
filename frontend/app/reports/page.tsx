"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { AppShell } from "../../components/layout/app-shell";
import { SearchInput } from "../../components/ui/search-input";
import { Button } from "../../components/ui/button";
import { EmptyState } from "../../components/ui/empty-state";
import { useAuth } from "../../lib/supabase/auth-context";
import { getRegisteredDocuments, RegisteredDocument } from "../../lib/document-registry";
import { getDocumentReport, USE_MOCKS } from "../../services/api";
import { VerificationReport } from "../../types";
import {
  FileText,
  Download,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
} from "lucide-react";

export default function ReportsListPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<RegisteredDocument[]>([]);
  const [reportsMap, setReportsMap] = useState<Record<string, VerificationReport>>({});
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

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
      getDocumentReport(mockDoc.document_id)
        .then((rep) => setReportsMap({ [mockDoc.document_id]: rep }))
        .finally(() => setIsLoading(false));
      return;
    }

    Promise.all(
      docs.map(async (doc) => {
        try {
          const rep = await getDocumentReport(doc.document_id);
          return { id: doc.document_id, rep };
        } catch {
          return null;
        }
      })
    ).then((res) => {
      const map: Record<string, VerificationReport> = {};
      res.forEach((r) => {
        if (r && r.rep) map[r.id] = r.rep;
      });
      setReportsMap(map);
      setIsLoading(false);
    });
  }, [user]);

  const filteredDocs = documents.filter((d) =>
    !search.trim() || d.filename.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppShell>
      <div className="space-y-6 pb-16">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
          <div>
            <h2 className="text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
              Verification Reports
            </h2>
            <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
              Synthesized academic integrity reports for verified manuscripts
            </p>
          </div>
          <div className="w-full sm:w-64">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder="Filter reports by filename..."
            />
          </div>
        </div>

        {/* Reports Table or Empty State */}
        {filteredDocs.length > 0 ? (
          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#F0E4D2] dark:border-[#3D322A] text-[#7A685D] dark:text-[#B8A898]">
                    <th className="py-3 font-semibold">Manuscript Name</th>
                    <th className="py-3 font-semibold">Verified Date</th>
                    <th className="py-3 font-semibold text-center">Total Claims</th>
                    <th className="py-3 font-semibold text-center">Supported</th>
                    <th className="py-3 font-semibold text-center">Flagged</th>
                    <th className="py-3 font-semibold text-center">Reliability Score</th>
                    <th className="py-3 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#F0E4D2]/60 dark:divide-[#3D322A]/60">
                  {filteredDocs.map((doc) => {
                    const rep = reportsMap[doc.document_id];
                    const dateStr = new Date(doc.uploaded_at).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      year: "numeric",
                    });

                    const supported = rep?.verdict_counts?.SUPPORTED ?? "—";
                    const flagged = rep
                      ? (rep.verdict_counts?.PARTLY_SUPPORTED || 0) +
                        (rep.verdict_counts?.UNSUPPORTED || 0) +
                        (rep.verdict_counts?.CONTRADICTORY || 0) +
                        (rep.human_review_required_count || 0)
                      : "—";

                    return (
                      <tr key={doc.document_id} className="hover:bg-[#FFF0D6]/30 dark:hover:bg-[#33291F]/30">
                        <td className="py-3.5 font-medium text-[#3E2F27] dark:text-[#F3E9DD] max-w-xs truncate">
                          📄 {doc.filename}
                        </td>
                        <td className="py-3.5 text-[#7A685D] dark:text-[#B8A898]">{dateStr}</td>
                        <td className="py-3.5 text-center font-mono tabular-nums">
                          {rep?.total_claims ?? "—"}
                        </td>
                        <td className="py-3.5 text-center font-mono tabular-nums text-emerald-700 dark:text-emerald-400 font-semibold">
                          {supported}
                        </td>
                        <td className="py-3.5 text-center font-mono tabular-nums text-rose-700 dark:text-rose-400 font-semibold">
                          {flagged}
                        </td>
                        <td className="py-3.5 text-center">
                          {rep?.reliability_score !== undefined ? (
                            <span className="font-mono font-bold px-2 py-0.5 rounded bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8]">
                              {rep.reliability_score.toFixed(1)}%
                            </span>
                          ) : (
                            <span className="text-[#A08B78]">In Progress</span>
                          )}
                        </td>
                        <td className="py-3.5 text-right">
                          <Link href={`/reports/${doc.document_id}`}>
                            <Button variant="primary" size="compact" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                              View Report
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : !isLoading ? (
          <EmptyState
            title="No reports available"
            description="Reports become available once a document finishes the automated verification pipeline."
            actionLabel="Start a new verification"
            onAction={() => window.location.assign("/verify")}
          />
        ) : null}
      </div>
    </AppShell>
  );
}
