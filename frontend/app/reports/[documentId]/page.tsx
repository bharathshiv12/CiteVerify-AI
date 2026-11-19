"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { AppShell } from "../../../components/layout/app-shell";
import { useDocumentReport, useDocumentStatus } from "../../../hooks/use-document";
import { downloadReportPdf } from "../../../services/api";
import { VerdictBadge, EvidenceLevelBadge, RetrievalBadge } from "../../../components/ui/status-badge";
import { ConfidenceIndicator } from "../../../components/verification/confidence-indicator";
import { Button } from "../../../components/ui/button";
import { Spinner } from "../../../components/ui/spinner";
import { ErrorState } from "../../../components/ui/error-state";
import {
  FileText,
  Printer,
  Download,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  BookOpen,
  ArrowLeft,
  Info,
} from "lucide-react";

export default function DocumentReportPage() {
  const params = useParams();
  const documentId = (params?.documentId as string) || "";

  const { data: statusData } = useDocumentStatus(documentId);
  const { data: report, isLoading, error, refetch } = useDocumentReport(documentId);

  // JSON Download handler
  const handleDownloadJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `citeverify_report_${report.document_id.slice(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Browser Print / Save as PDF handler
  const handlePrint = () => {
    window.print();
  };

  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const handleDownloadPdf = async () => {
    try {
      setIsDownloadingPdf(true);
      const blob = await downloadReportPdf(documentId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `citeverify_report_${report?.document_id.slice(0, 8) || "export"}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("PDF download failed", e);
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  if (isLoading) {
    return (
      <AppShell>
        <div className="py-20 flex flex-col items-center justify-center space-y-4">
          <Spinner size="lg" />
          <p className="text-sm font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">
            Synthesizing verification report...
          </p>
        </div>
      </AppShell>
    );
  }

  if (error || !report) {
    const isConflict = statusData?.status === "PROCESSING" || statusData?.status === "PENDING";
    return (
      <AppShell>
        <div className="max-w-2xl mx-auto py-12 space-y-4">
          {isConflict ? (
            <div className="p-8 rounded-[16px] bg-[#FFF0D6] dark:bg-[#33291F] border border-[#F4B860] text-center space-y-3">
              <Spinner size="md" className="mx-auto" />
              <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                Verification Analysis in Progress (HTTP 409)
              </h3>
              <p className="text-xs text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
                The verification report is synthesized only after the verification engine completes. The pipeline is currently at{" "}
                <strong>{statusData?.pipeline_stage}</strong> ({statusData?.progress_percent}%).
              </p>
              <div className="pt-4 flex items-center justify-center gap-3">
                <Link href={`/verify/${documentId}/extract`}>
                  <Button variant="primary" size="compact">
                    View Real-time Stage Progress
                  </Button>
                </Link>
                <Button variant="outline" size="compact" onClick={() => refetch()}>
                  Refresh Report Status
                </Button>
              </div>
            </div>
          ) : (
            <ErrorState
              title="Report unavailable"
              message={error instanceof Error ? error.message : "Unable to retrieve report from server."}
              onRetry={() => refetch()}
            />
          )}
        </div>
      </AppShell>
    );
  }

  const generatedDate = new Date(report.generated_at).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const categories = [
    { label: "Supported", count: report.verdict_counts?.SUPPORTED || 0, color: "#39765B" },
    { label: "Partially Supported", count: report.verdict_counts?.PARTLY_SUPPORTED || 0, color: "#B68A42" },
    { label: "Unsupported", count: report.verdict_counts?.UNSUPPORTED || 0, color: "#B94D4D" },
    { label: "Contradictory", count: report.verdict_counts?.CONTRADICTORY || 0, color: "#74518C" },
    { label: "Potentially Outdated", count: report.verdict_counts?.POTENTIALLY_OUTDATED || 0, color: "#B77B35" },
    { label: "Needs Human Review", count: report.human_review_required_count || 0, color: "#766F68" },
  ];

  return (
    <AppShell>
      <div className="space-y-8 pb-16">
        {/* Navigation & Actions Bar (Hidden on Print) */}
        <div className="no-print flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 p-4 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
          <Link
            href="/reports"
            className="inline-flex items-center gap-1.5 text-xs text-[#8D6E63] dark:text-[#D7B8A8] font-semibold hover:underline"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Reports List
          </Link>

          <div className="flex flex-wrap items-center gap-2.5">
            <Button
              variant="outline"
              size="compact"
              onClick={handlePrint}
              leftIcon={<Printer className="w-3.5 h-3.5" />}
            >
              Print / Save
            </Button>
            <Button
              variant="secondary"
              size="compact"
              onClick={handleDownloadJSON}
              leftIcon={<Download className="w-3.5 h-3.5" />}
            >
              JSON
            </Button>
            <Button
              variant="primary"
              size="compact"
              onClick={handleDownloadPdf}
              isLoading={isDownloadingPdf}
              leftIcon={<FileText className="w-3.5 h-3.5" />}
            >
              Download PDF Report
            </Button>
          </div>
        </div>

        {/* Printable Report Container */}
        <article className="card-print p-6 sm:p-10 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-8">
          {/* 1. Document Overview Header */}
          <div className="border-b border-[#F0E4D2] dark:border-[#3D322A] pb-6 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#8D6E63] dark:text-[#D7B8A8] flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-[#39765B]" />
                CiteVerify AI Academic Integrity Report
              </span>
              <span className="text-xs font-mono text-[#7A685D] dark:text-[#B8A898]">
                ID: {report.document_id.slice(0, 18)}...
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold font-heading text-[#3E2F27] dark:text-[#F3E9DD]">
              {report.filename}
            </h1>
            <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
              Verified on {generatedDate} • Total Claims Evaluated: <strong>{report.total_claims}</strong>
            </p>
          </div>

          {/* 2. Reliability & Verdict Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-[14px] bg-[#FFF0D6]/40 dark:bg-[#33291F]/40 border border-[#F4B860]/40 flex flex-col justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#8D6E63] dark:text-[#D7B8A8]">
                  Empirical Reliability Score
                </span>
                <div className="text-4xl font-extrabold font-heading text-[#3E2F27] dark:text-[#F3E9DD] tabular-nums mt-2">
                  {report.reliability_score.toFixed(1)}%
                </div>
              </div>
              <p className="mt-4 text-[11px] text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
                Reflects the weighted proportion of empirical statements confirmed by retrieved scholarly evidence passages.
              </p>
            </div>

            <div className="md:col-span-2 p-6 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-sm">
              <span className="text-xs font-bold uppercase tracking-wider text-[#8D6E63] dark:text-[#D7B8A8] block mb-3">
                Verdict Distribution:
              </span>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {categories.map((c) => (
                  <div key={c.label} className="p-2.5 rounded-[8px] bg-[#FFF8E8]/70 dark:bg-[#1E1814]/70 border border-[#F0E4D2] dark:border-[#3D322A]">
                    <div className="flex items-center gap-1.5 text-xs font-medium text-[#7A685D] dark:text-[#B8A898]">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c.color }} />
                      <span className="truncate">{c.label}</span>
                    </div>
                    <p className="text-lg font-bold text-[#3E2F27] dark:text-[#F3E9DD] tabular-nums mt-0.5">
                      {c.count}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 3. Claim-by-Claim Verification Audit */}
          <div className="space-y-6 pt-4 border-t border-[#F0E4D2] dark:border-[#3D322A]">
            <div>
              <h2 className="text-lg font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
                Claim-by-Claim Audit Trail
              </h2>
              <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                Itemized analysis comparing each scientific assertion against retrieved publication evidence
              </p>
            </div>

            <div className="space-y-6">
              {report.claims && report.claims.length > 0 ? (
                report.claims.map((claim, idx) => (
                  <div
                    key={claim.id || idx}
                    className="p-5 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-sm space-y-4"
                  >
                    {/* Claim Header */}
                    <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[#F0E4D2]/60 dark:border-[#3D322A]/60">
                      <span className="font-bold text-xs font-mono text-[#8D6E63] dark:text-[#D7B8A8]">
                        Claim #{idx + 1} • Manuscript Page {claim.page_number}
                      </span>
                      <div className="flex items-center gap-2">
                        <VerdictBadge verdict={claim.verdict} />
                        <ConfidenceIndicator confidence={claim.confidence} showBar={false} />
                      </div>
                    </div>

                    {/* Claim Text */}
                    <blockquote className="p-3.5 rounded-[8px] bg-[#FFF8E8] dark:bg-[#1E1814] border-l-4 border-[#F4B860] text-xs sm:text-sm font-medium text-[#3E2F27] dark:text-[#F3E9DD] italic leading-relaxed">
                      &ldquo;{claim.claim_text}&rdquo;
                    </blockquote>

                    {/* Verification Rationale */}
                    {claim.rationale && (
                      <div className="text-xs text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
                        <strong className="text-[#3E2F27] dark:text-[#F3E9DD]">Rationale: </strong>
                        {claim.rationale}
                      </div>
                    )}

                    {/* Retrieved Evidence Passages */}
                    {claim.evidence && claim.evidence.length > 0 ? (
                      <div className="space-y-2 pt-2 border-t border-[#F0E4D2]/40 dark:border-[#3D322A]/40">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-[#8D6E63] dark:text-[#D7B8A8]">
                          Retrieved Source Evidence:
                        </span>
                        {claim.evidence.map((ev, eIdx) => (
                          <div
                            key={ev.id || eIdx}
                            className="p-3 rounded-[8px] bg-[#FFF8E8]/60 dark:bg-[#1E1814]/60 border border-[#F0E4D2] dark:border-[#3D322A] text-xs space-y-1.5"
                          >
                            <div className="flex items-center justify-between text-[11px]">
                              <div className="flex items-center gap-2">
                                <EvidenceLevelBadge level={ev.evidence_level} />
                                <span className="font-mono text-[#7A685D] dark:text-[#B8A898]">
                                  {ev.source_provider}
                                </span>
                              </div>
                              {ev.doi && (
                                <a
                                  href={`https://doi.org/${ev.doi}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="font-mono text-[#8D6E63] hover:underline flex items-center gap-1"
                                >
                                  doi:{ev.doi} <ExternalLink className="w-3 h-3" />
                                </a>
                              )}
                            </div>
                            <p className="text-[#3E2F27] dark:text-[#F3E9DD] italic leading-relaxed">
                              &ldquo;{ev.passage}&rdquo;
                            </p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-3 rounded-[8px] bg-[#FFF0D6]/30 dark:bg-[#33291F]/30 text-xs text-[#7A685D] dark:text-[#B8A898] italic">
                        No evidence passage could be retrieved for this citation.
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-xs text-[#7A685D] dark:text-[#B8A898] italic">
                  No claims found in report payload.
                </p>
              )}
            </div>
          </div>

          {/* 4. Methodology Limitations & Integrity Notice */}
          <div className="print-page-break p-6 rounded-[14px] bg-[#FFF0D6]/40 dark:bg-[#33291F]/40 border border-[#F0E4D2] dark:border-[#3D322A] text-xs space-y-2">
            <h3 className="font-bold text-sm text-[#8D6E63] dark:text-[#D7B8A8] flex items-center gap-1.5">
              <Info className="w-4 h-4 text-[#8D6E63]" />
              Methodology Limitations & Scientific Traceability
            </h3>
            <ul className="list-disc list-inside space-y-1 text-[11px] text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
              <li>
                <strong>Evidence Dependency:</strong> Verdicts reflect only retrieved source material. Failure to retrieve a paper (due to paywalls, API limits, or index omissions) does not constitute disproof of the claim.
              </li>
              <li>
                <strong>Evidence Level Transparency:</strong> Abstracts are never evaluated or presented as full text. Claims marked with <code>ABSTRACT_ONLY</code> require full-text verification for experimental nuance.
              </li>
              <li>
                <strong>Human-in-the-Loop:</strong> Claims flagged with <code>Needs Human Review</code> or null verdicts represent ambiguous assertions requiring domain specialist review.
              </li>
            </ul>
          </div>
        </article>
      </div>
    </AppShell>
  );
}
