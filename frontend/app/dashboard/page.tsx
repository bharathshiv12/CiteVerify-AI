"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "../../components/layout/app-shell";
import { StatCard } from "../../components/ui/stat-card";
import { Button } from "../../components/ui/button";
import { EmptyState } from "../../components/ui/empty-state";
import { VerdictBadge } from "../../components/ui/status-badge";
import { useAuth } from "../../lib/supabase/auth-context";
import { getRegisteredDocuments, registerDocument, RegisteredDocument } from "../../lib/document-registry";
import { getDocumentReport, getDocumentStatus, listDocuments, USE_MOCKS } from "../../services/api";
import { VerificationReport, DocumentStatusResponse } from "../../types";
import {
  FileCheck,
  FileText,
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowRight,
  ExternalLink,
  PieChart as PieChartIcon,
} from "lucide-react";

export default function DashboardPage() {
  const { fullName, user } = useAuth();
  const [greeting, setGreeting] = useState("Good morning");
  const [documents, setDocuments] = useState<RegisteredDocument[]>([]);
  const [reportsMap, setReportsMap] = useState<Record<string, VerificationReport>>({});
  const [statusMap, setStatusMap] = useState<Record<string, DocumentStatusResponse>>({});
  const [isLoading, setIsLoading] = useState(true);

  // Time-based academic greeting
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);

  // Load documents from device registry and fetch live reports
  useEffect(() => {
    async function loadDashboard() {
      let docs = getRegisteredDocuments(user?.id);

      if (user && !USE_MOCKS) {
        try {
          const remote = await listDocuments(1, 50);
          if (remote?.items?.length) {
            remote.items.forEach((rd) => {
              registerDocument(
                {
                  document_id: rd.id,
                  filename: rd.filename,
                  uploaded_at: rd.created_at,
                  file_size_bytes: rd.file_size_bytes,
                  status: rd.status,
                  pipeline_stage: rd.pipeline_stage,
                },
                user.id
              );
            });
            docs = getRegisteredDocuments(user.id);
          }
        } catch {}
      }

      setDocuments(docs);

      if (docs.length === 0 && !USE_MOCKS) {
        setIsLoading(false);
        return;
      }

      // In mock mode, if no docs exist, synthesize one from examples
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

      // Query real reports & statuses for registered documents
      Promise.all(
        docs.map(async (doc) => {
          try {
            const rep = await getDocumentReport(doc.document_id);
            return { id: doc.document_id, rep };
          } catch {
            return null;
          }
        })
      ).then((results) => {
        const map: Record<string, VerificationReport> = {};
        results.forEach((r) => {
          if (r && r.rep) map[r.id] = r.rep;
        });
        setReportsMap(map);
        setIsLoading(false);
      });
    }

    loadDashboard();
  }, [user]);

  // Derive aggregate metrics strictly from real data
  const totalDocs = documents.length;
  let totalClaims = 0;
  let supportedClaims = 0;
  let partlySupported = 0;
  let unsupported = 0;
  let contradictory = 0;
  let outdated = 0;
  let needsReview = 0;

  Object.values(reportsMap).forEach((rep) => {
    totalClaims += rep.total_claims || 0;
    supportedClaims += rep.verdict_counts?.SUPPORTED || 0;
    partlySupported += rep.verdict_counts?.PARTLY_SUPPORTED || 0;
    unsupported += rep.verdict_counts?.UNSUPPORTED || 0;
    contradictory += rep.verdict_counts?.CONTRADICTORY || 0;
    outdated += rep.verdict_counts?.POTENTIALLY_OUTDATED || 0;
    needsReview += rep.human_review_required_count || 0;
  });

  const flaggedClaims = partlySupported + unsupported + contradictory + outdated + needsReview;

  const categories = [
    { label: "Supported", count: supportedClaims, color: "#39765B" },
    { label: "Partially Supported", count: partlySupported, color: "#B68A42" },
    { label: "Unsupported", count: unsupported, color: "#B94D4D" },
    { label: "Contradictory", count: contradictory, color: "#74518C" },
    { label: "Potentially Outdated", count: outdated, color: "#B77B35" },
    { label: "Needs Human Review", count: needsReview, color: "#766F68" },
  ];

  return (
    <AppShell>
      <div className="space-y-8 pb-12">
        {/* Top Greeting & Header Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
          <div>
            <h2 className="text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
              {greeting}, {fullName || "Researcher"}
            </h2>
            <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
              Your research verification workspace is ready.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/verify">
              <Button variant="primary" size="compact" leftIcon={<FileCheck className="w-3.5 h-3.5" />}>
                New Verification
              </Button>
            </Link>
            <Link href="/reports">
              <Button variant="secondary" size="compact" leftIcon={<FileText className="w-3.5 h-3.5" />}>
                View Reports
              </Button>
            </Link>
          </div>
        </div>

        {/* 4 Primary Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Documents Analyzed"
            value={totalDocs}
            subtitle="Registered on this device"
            icon={<FileText className="w-5 h-5" />}
            accentColor="#F4B860"
          />
          <StatCard
            title="Claims Extracted"
            value={totalClaims}
            subtitle="Across verified manuscripts"
            icon={<CheckCircle2 className="w-5 h-5" />}
            accentColor="#39765B"
          />
          <StatCard
            title="Supported Claims"
            value={supportedClaims}
            subtitle={totalClaims > 0 ? `${Math.round((supportedClaims / totalClaims) * 100)}% verified` : "0%"}
            icon={<CheckCircle2 className="w-5 h-5" />}
            accentColor="#39765B"
          />
          <StatCard
            title="Flagged Claims"
            value={flaggedClaims}
            subtitle="Requires human audit"
            tooltip="Flagged means any verdict other than SUPPORTED, including needs-review states."
            icon={<AlertTriangle className="w-5 h-5" />}
            accentColor="#B94D4D"
          />
        </div>

        {/* Empty State when no documents exist */}
        {totalDocs === 0 && !isLoading && (
          <EmptyState
            title="No verified documents yet"
            description="CiteVerify analyzes academic PDF papers, extracts factual claims, links attached citations to scholarly indexes, and compares source evidence."
            actionLabel="Verify your first document"
            onAction={() => window.location.assign("/verify")}
            icon={<UploadCloud className="w-8 h-8" />}
          />
        )}

        {totalDocs > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Claim Verification Overview (Donut Breakdown) */}
            <div className="lg:col-span-1 p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8] flex items-center gap-2 mb-1">
                  <PieChartIcon className="w-4 h-4" />
                  Claim Verification Overview
                </h3>
                <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                  Evidence distribution across all extracted claims
                </p>
              </div>

              {/* Accessible Legend & Counts */}
              <div className="my-6 space-y-2.5">
                {categories.map((c) => {
                  const pct = totalClaims > 0 ? Math.round((c.count / totalClaims) * 100) : 0;
                  return (
                    <div key={c.label} className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: c.color }}
                        />
                        <span className="font-medium text-[#3E2F27] dark:text-[#F3E9DD]">
                          {c.label}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 tabular-nums">
                        <span className="font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                          {c.count}
                        </span>
                        <span className="text-[11px] text-[#7A685D] dark:text-[#B8A898] w-8 text-right">
                          ({pct}%)
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="pt-3 border-t border-[#F0E4D2] dark:border-[#3D322A] flex items-center justify-between text-xs text-[#7A685D] dark:text-[#B8A898]">
                <span>Total Extracted Claims</span>
                <span className="font-extrabold text-sm text-[#3E2F27] dark:text-[#F3E9DD] tabular-nums">
                  {totalClaims}
                </span>
              </div>
            </div>

            {/* Recent Verifications Table */}
            <div className="lg:col-span-2 p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
                    Recent Verifications
                  </h3>
                  <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                    Latest research papers verified on this device
                  </p>
                </div>
                <Link
                  href="/history"
                  className="text-xs font-semibold text-[#8D6E63] hover:text-[#3E2F27] dark:text-[#D7B8A8] dark:hover:text-[#F3E9DD] underline flex items-center gap-1"
                >
                  View All History <ArrowRight className="w-3 h-3" />
                </Link>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-[#F0E4D2] dark:border-[#3D322A] text-[#7A685D] dark:text-[#B8A898]">
                      <th className="py-2.5 font-semibold">Document Name</th>
                      <th className="py-2.5 font-semibold">Verified</th>
                      <th className="py-2.5 font-semibold text-center">Claims</th>
                      <th className="py-2.5 font-semibold text-center">Supported</th>
                      <th className="py-2.5 font-semibold text-center">Flagged</th>
                      <th className="py-2.5 font-semibold text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F0E4D2]/60 dark:divide-[#3D322A]/60">
                    {documents.slice(0, 5).map((d) => {
                      const rep = reportsMap[d.document_id];
                      const dateStr = new Date(d.uploaded_at).toLocaleDateString("en-IN", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      });

                      const docSupported = rep?.verdict_counts?.SUPPORTED ?? "-";
                      const docFlagged =
                        rep
                          ? (rep.verdict_counts?.PARTLY_SUPPORTED || 0) +
                            (rep.verdict_counts?.UNSUPPORTED || 0) +
                            (rep.verdict_counts?.CONTRADICTORY || 0) +
                            (rep.human_review_required_count || 0)
                          : "-";

                      return (
                        <tr key={d.document_id} className="hover:bg-[#FFF0D6]/30 dark:hover:bg-[#33291F]/30">
                          <td className="py-3 font-medium text-[#3E2F27] dark:text-[#F3E9DD] max-w-[200px] truncate">
                            📄 {d.filename}
                          </td>
                          <td className="py-3 text-[#7A685D] dark:text-[#B8A898]">{dateStr}</td>
                          <td className="py-3 text-center tabular-nums font-mono">
                            {rep ? rep.total_claims : "—"}
                          </td>
                          <td className="py-3 text-center tabular-nums text-emerald-700 dark:text-emerald-400 font-semibold font-mono">
                            {docSupported}
                          </td>
                          <td className="py-3 text-center tabular-nums text-rose-700 dark:text-rose-400 font-semibold font-mono">
                            {docFlagged}
                          </td>
                          <td className="py-3 text-right">
                            <Link href={`/reports/${d.document_id}`}>
                              <Button variant="outline" size="compact">
                                Report
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
          </div>
        )}

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            href="/verify"
            className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand hover:border-[#F4B860] transition-colors group"
          >
            <div className="w-10 h-10 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center mb-3 group-hover:bg-[#F4B860] group-hover:text-[#3E2F27] transition-colors">
              <UploadCloud className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
              Upload Research Document
            </h4>
            <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
              Drag and drop an academic PDF to initiate automated claim extraction.
            </p>
          </Link>

          <Link
            href="/reports"
            className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand hover:border-[#F4B860] transition-colors group"
          >
            <div className="w-10 h-10 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center mb-3 group-hover:bg-[#F4B860] group-hover:text-[#3E2F27] transition-colors">
              <FileText className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
              View Verification Reports
            </h4>
            <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
              Inspect synthesized reliability scores and claim-by-claim citations.
            </p>
          </Link>

          <Link
            href="/history"
            className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand hover:border-[#F4B860] transition-colors group"
          >
            <div className="w-10 h-10 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center mb-3 group-hover:bg-[#F4B860] group-hover:text-[#3E2F27] transition-colors">
              <Clock className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
              Device Verification History
            </h4>
            <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
              Browse past audits and continue pending verification workflows.
            </p>
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
