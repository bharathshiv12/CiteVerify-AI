import React from "react";
import Link from "next/link";
import { Logo } from "../../components/brand/logo";
import { ArrowLeft } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] py-12 px-4 sm:px-6 lg:px-8 text-[#3E2F27] dark:text-[#F3E9DD]">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between pb-6 border-b border-[#F0E4D2] dark:border-[#3D322A]">
          <Logo size="md" />
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 text-xs text-[#8D6E63] dark:text-[#D7B8A8] font-semibold hover:underline"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Return
          </Link>
        </div>

        <div className="p-8 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
              Terms of Service
            </h1>
            <span className="text-xs uppercase tracking-wider font-bold bg-[#FFDCA8] text-[#3E2F27] px-2.5 py-1 rounded-full">
              Draft Prototype
            </span>
          </div>

          <div className="text-xs text-[#7A685D] dark:text-[#B8A898] space-y-4 leading-relaxed">
            <p>
              <strong>1. Hackathon Demonstration Prototype:</strong> CiteVerify AI is developed as an academic verification prototype for the INNOVEDGE 2026 Hackathon (Problem Statement 03). It is intended for research analysis and evaluation purposes.
            </p>
            <p>
              <strong>2. PDF Document Processing:</strong> When you upload scientific research PDF files, our backend pipeline extracts textual statements, in-text citation markers, and bibliography references. Uploaded files are processed strictly for citation verification and evidence passage extraction against public scholarly indexes (Crossref, OpenAlex, and Europe PMC).
            </p>
            <p>
              <strong>3. Evidence Traceability & Reliability:</strong> CiteVerify provides automated claim-to-evidence comparisons and natural language inference metrics. Automated verdicts reflect retrieved evidence strength and do not constitute absolute truth certification or legal guarantees.
            </p>
            <p>
              <strong>4. User Accounts:</strong> User authentication and profile metadata are managed via Supabase. We do not sell user data, personal details, or uploaded academic documents.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
