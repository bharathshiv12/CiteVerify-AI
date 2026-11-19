import React from "react";
import Link from "next/link";
import { Logo } from "../../components/brand/logo";
import { ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
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
              Privacy Policy
            </h1>
            <span className="text-xs uppercase tracking-wider font-bold bg-[#FFDCA8] text-[#3E2F27] px-2.5 py-1 rounded-full">
              Draft Prototype
            </span>
          </div>

          <div className="text-xs text-[#7A685D] dark:text-[#B8A898] space-y-4 leading-relaxed">
            <p>
              <strong>1. Data Collection:</strong> We collect your academic email, name, and institution when you register for an account using Supabase Auth. Device history is stored locally in your browser storage.
            </p>
            <p>
              <strong>2. Academic Paper Usage:</strong> Academic PDF papers uploaded to CiteVerify are processed solely by the automated verification pipeline to extract claims, identify citations, and compare findings against public scholarly APIs (Crossref, OpenAlex, and Europe PMC).
            </p>
            <p>
              <strong>3. No Sale of Information:</strong> Under no circumstances is personal user data or uploaded manuscript text sold, monetized, or shared with third-party advertisers.
            </p>
            <p>
              <strong>4. Data Retention & Device Purging:</strong> Users may remove document records from their device history at any time through the History interface.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
