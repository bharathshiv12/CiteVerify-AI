"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Logo } from "../components/brand/logo";
import { Button } from "../components/ui/button";
import { checkHealth, USE_MOCKS } from "../services/api";
import {
  FileCheck,
  ShieldCheck,
  Search,
  BookOpen,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Activity,
  Layers,
} from "lucide-react";

export default function HomePage() {
  const [healthInfo, setHealthInfo] = useState<{
    status: string;
    service?: string;
    version?: string;
  }>({ status: "checking" });

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "") ||
    process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/+$/, "") ||
    "http://localhost:8000";

  useEffect(() => {
    checkHealth()
      .then((data) => setHealthInfo({ status: "online", service: data.service, version: data.version }))
      .catch(() => setHealthInfo({ status: "offline" }));
  }, []);

  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] text-[#3E2F27] dark:text-[#F3E9DD] flex flex-col">
      {/* Top Navbar */}
      <header className="w-full border-b border-[#F0E4D2] dark:border-[#3D322A] bg-white/70 dark:bg-[#2A221C]/70 backdrop-blur-md sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Logo size="md" />
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="outline" size="compact">
                Sign In
              </Button>
            </Link>
            <Link href="/verify">
              <Button variant="primary" size="compact" rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
                Verify Document
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20 flex flex-col items-center text-center">
        {/* Core Principle Pill */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#FFF0D6] dark:bg-[#33291F] border border-[#F4B860]/50 text-xs font-semibold text-[#8D6E63] dark:text-[#D7B8A8] mb-6 shadow-sm">
          <ShieldCheck className="w-4 h-4 text-[#39765B]" />
          <span>Core Principle: A real citation does not automatically support its claim.</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8] tracking-tight max-w-4xl leading-[1.15]">
          Verify the Claim. <br className="hidden sm:inline" />
          <span className="text-[#3E2F27] dark:text-[#F3E9DD]">Trace the Evidence. </span>
          Trust the Research.
        </h1>

        <p className="mt-5 text-sm sm:text-lg text-[#7A685D] dark:text-[#B8A898] max-w-2xl leading-relaxed">
          An automated, evidence-first academic claim and citation verification platform. Evaluate whether scientific claims are genuinely supported by cited literature retrieved via Crossref, OpenAlex, and Europe PMC.
        </p>

        {/* Primary CTA Buttons */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <Link href="/verify">
            <Button variant="primary" size="mobile" rightIcon={<FileCheck className="w-4 h-4" />}>
              Start Document Verification
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button variant="secondary" size="mobile">
              Open Research Workspace
            </Button>
          </Link>
        </div>

        {/* Live Backend Status Badge */}
        <div className="mt-8 inline-flex items-center gap-2 text-xs text-[#7A685D] dark:text-[#B8A898] bg-white dark:bg-[#2A221C] px-3.5 py-1.5 rounded-full border border-[#F0E4D2] dark:border-[#3D322A]">
          <Activity className="w-3.5 h-3.5 text-[#8D6E63]" />
          <span>Backend Status ({apiBaseUrl}):</span>
          <span
            className={`font-mono px-2 py-0.5 rounded text-[11px] font-semibold ${
              healthInfo.status === "online"
                ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300"
                : healthInfo.status === "checking"
                ? "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
                : "bg-stone-200 text-stone-700 dark:bg-stone-800 dark:text-stone-300"
            }`}
          >
            {healthInfo.status === "online"
              ? `Online (${healthInfo.service || "backend"} v${healthInfo.version || "1.0.0"})`
              : healthInfo.status === "checking"
              ? "Checking..."
              : "Offline / Standalone"}
          </span>
          {USE_MOCKS && (
            <span className="font-mono text-[10px] bg-[#F4B860] text-[#3E2F27] px-1.5 py-0.5 rounded font-bold uppercase">
              Mock Enabled
            </span>
          )}
        </div>

        {/* Pipeline Highlights Grid */}
        <div className="mt-16 sm:mt-24 w-full grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-3">
            <div className="w-10 h-10 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold font-heading text-[#3E2F27] dark:text-[#F3E9DD]">
              1. Claim & Citation Extraction
            </h3>
            <p className="text-xs text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
              Accepts academic PDF manuscripts, extracts factual assertions, maps numeric and author-year citation markers, and parses the complete bibliography.
            </p>
          </div>

          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-3">
            <div className="w-10 h-10 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center">
              <Search className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold font-heading text-[#3E2F27] dark:text-[#F3E9DD]">
              2. Open Scholarly Retrieval
            </h3>
            <p className="text-xs text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
              Integrates with Crossref, OpenAlex, and Europe PMC to resolve cited papers, fetch legitimate open-access abstracts and full texts with clear evidence levels.
            </p>
          </div>

          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-3">
            <div className="w-10 h-10 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold font-heading text-[#3E2F27] dark:text-[#F3E9DD]">
              3. Evidence-First Verification
            </h3>
            <p className="text-xs text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
              Compares exact claim assertions against source passages using semantic ranking and NLI models. Produces traceable verdicts with confidence scores and audit logs.
            </p>
          </div>
        </div>

        {/* Scientific Honesty Commitments */}
        <div className="mt-16 w-full p-6 sm:p-8 rounded-[16px] bg-white/70 dark:bg-[#2A221C]/70 border border-[#F0E4D2] dark:border-[#3D322A] text-left">
          <h3 className="text-sm font-bold uppercase tracking-wider text-[#8D6E63] dark:text-[#D7B8A8] mb-4 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#39765B]" />
            Scientific Integrity & Honesty Rules
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs text-[#7A685D] dark:text-[#B8A898]">
            <div className="p-3 bg-[#FFF8E8] dark:bg-[#1E1814] rounded-[10px] border border-[#F0E4D2] dark:border-[#3D322A]">
              <strong className="block text-[#3E2F27] dark:text-[#F3E9DD] mb-1">Never Fabricate</strong>
              Zero invented DOIs, publications, evidence passages, citations, or benchmark results.
            </div>
            <div className="p-3 bg-[#FFF8E8] dark:bg-[#1E1814] rounded-[10px] border border-[#F0E4D2] dark:border-[#3D322A]">
              <strong className="block text-[#3E2F27] dark:text-[#F3E9DD] mb-1">Abstracts vs Full Text</strong>
              Abstracts are never labelled as full text. Every evidence item explicitly sets evidence level.
            </div>
            <div className="p-3 bg-[#FFF8E8] dark:bg-[#1E1814] rounded-[10px] border border-[#F0E4D2] dark:border-[#3D322A]">
              <strong className="block text-[#3E2F27] dark:text-[#F3E9DD] mb-1">Retrieval ≠ Refutation</strong>
              A paper that cannot be retrieved is not marked false; it is flagged for human review.
            </div>
            <div className="p-3 bg-[#FFF8E8] dark:bg-[#1E1814] rounded-[10px] border border-[#F0E4D2] dark:border-[#3D322A]">
              <strong className="block text-[#3E2F27] dark:text-[#F3E9DD] mb-1">No Coerced Verdicts</strong>
              Claims with insufficient evidence carry null verdict and prompt expert human review.
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-[#F0E4D2] dark:border-[#3D322A] py-6 px-4 sm:px-6 lg:px-8 bg-white/40 dark:bg-[#2A221C]/40 text-xs text-[#7A685D] dark:text-[#B8A898]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 CiteVerify AI — Built for INNOVEDGE 2026 Hackathon (Problem Statement 03).</p>
          <div className="flex items-center gap-4">
            <Link href="/terms" className="hover:underline">
              Terms of Service
            </Link>
            <Link href="/privacy" className="hover:underline">
              Privacy Policy
            </Link>
            <Link href="/design-system" className="hover:underline">
              Design System
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
