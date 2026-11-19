"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/layout/app-shell";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { PasswordInput } from "../../components/ui/password-input";
import { Select } from "../../components/ui/select";
import { Checkbox } from "../../components/ui/checkbox";
import { Textarea } from "../../components/ui/textarea";
import { VerdictBadge, CitationBadge, EvidenceLevelBadge, RetrievalBadge } from "../../components/ui/status-badge";
import { StatCard } from "../../components/ui/stat-card";
import { Spinner, Skeleton } from "../../components/ui/spinner";
import { ConfidenceIndicator } from "../../components/verification/confidence-indicator";
import { FileCheck, Sparkles, AlertCircle } from "lucide-react";

export default function DesignSystemPage() {
  const [testPassword, setTestPassword] = useState("ResearchPass2026!");
  const [testCheckbox, setTestCheckbox] = useState(true);

  // Exact brand colors specification display
  const brandColors = [
    { token: "--bg", hex: "#FFF8E8", name: "Main Canvas Background" },
    { token: "--card", hex: "#FFFFFF", name: "Card Surface" },
    { token: "--primary", hex: "#F4B860", name: "Primary Action Amber" },
    { token: "--secondary", hex: "#FFDCA8", name: "Secondary Action Amber" },
    { token: "--highlight", hex: "#FFF0D6", name: "Sidebar Highlight" },
    { token: "--heading", hex: "#8D6E63", name: "Section Title Brown" },
    { token: "--border", hex: "#F0E4D2", name: "Structural Border" },
  ];

  const derivedColors = [
    { token: "--ink", hex: "#3E2F27", name: "Primary Body & Button Text" },
    { token: "--ink-muted", hex: "#7A685D", name: "Muted Secondary Text" },
    { token: "--border-input", hex: "#A08B78", name: "Input & Ghost Border" },
    { token: "--focus", hex: "#8D6E63", name: "Keyboard Focus Ring" },
  ];

  return (
    <AppShell>
      <div className="space-y-10 pb-16">
        {/* Header */}
        <div className="p-6 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] text-xs font-bold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            Internal Living Styleguide & Component Showcase
          </div>
          <h2 className="text-2xl font-extrabold font-heading text-[#3E2F27] dark:text-[#F3E9DD]">
            CiteVerify AI Design System
          </h2>
          <p className="mt-1.5 text-sm text-[#7A685D] dark:text-[#B8A898] max-w-2xl">
            Locked brand tokens, typography scales, controlled button variants, semantic verification badges, and accessible form controls.
          </p>
        </div>

        {/* 1. Brand Tokens */}
        <section className="space-y-4">
          <h3 className="text-lg font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
            1. Immutable Brand Color Palette
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            {brandColors.map((c) => (
              <div
                key={c.token}
                className="p-3 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-sm flex flex-col items-center text-center"
              >
                <div
                  className="w-12 h-12 rounded-[10px] mb-2 border border-black/10 shadow-inner"
                  style={{ backgroundColor: c.hex }}
                />
                <span className="font-mono text-xs font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                  {c.hex}
                </span>
                <span className="font-mono text-[11px] text-[#8D6E63] dark:text-[#D7B8A8]">
                  {c.token}
                </span>
                <span className="text-[10px] text-[#7A685D] dark:text-[#B8A898] mt-1 leading-tight">
                  {c.name}
                </span>
              </div>
            ))}
          </div>

          <h4 className="text-sm font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8] pt-2">
            Derived Supporting Tokens
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {derivedColors.map((c) => (
              <div
                key={c.token}
                className="p-3 rounded-[12px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-sm flex flex-col items-center text-center"
              >
                <div
                  className="w-10 h-10 rounded-[10px] mb-2 border border-black/10 shadow-inner"
                  style={{ backgroundColor: c.hex }}
                />
                <span className="font-mono text-xs font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                  {c.hex}
                </span>
                <span className="font-mono text-[11px] text-[#8D6E63] dark:text-[#D7B8A8]">
                  {c.token}
                </span>
                <span className="text-[10px] text-[#7A685D] dark:text-[#B8A898] mt-1 leading-tight">
                  {c.name}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* 2. Semantic Badges */}
        <section className="space-y-4">
          <h3 className="text-lg font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
            2. Semantic Verification & Citation Badges
          </h3>
          <div className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[#7A685D] dark:text-[#B8A898] mb-2">
                Verification Verdicts:
              </p>
              <div className="flex flex-wrap gap-2.5">
                <VerdictBadge verdict="SUPPORTED" />
                <VerdictBadge verdict="PARTLY_SUPPORTED" />
                <VerdictBadge verdict="UNSUPPORTED" />
                <VerdictBadge verdict="CONTRADICTORY" />
                <VerdictBadge verdict="POTENTIALLY_OUTDATED" />
                <VerdictBadge verdict={null} />
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[#7A685D] dark:text-[#B8A898] mb-2">
                Citation Mapping Status:
              </p>
              <div className="flex flex-wrap gap-2.5">
                <CitationBadge status="MATCHED" />
                <CitationBadge status="PARTIALLY_MATCHED" />
                <CitationBadge status="UNMATCHED" />
                <CitationBadge status="MISSING_REFERENCE" />
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[#7A685D] dark:text-[#B8A898] mb-2">
                Evidence Levels & Retrieval Status:
              </p>
              <div className="flex flex-wrap gap-2.5">
                <EvidenceLevelBadge level="FULL_TEXT" />
                <EvidenceLevelBadge level="ABSTRACT_ONLY" />
                <EvidenceLevelBadge level="METADATA_ONLY" />
                <EvidenceLevelBadge level="NONE" />
                <RetrievalBadge status="RETRIEVED" />
                <RetrievalBadge status="PAYWALLED" />
                <RetrievalBadge status="NOT_FOUND" />
                <RetrievalBadge status="API_ERROR" />
              </div>
            </div>
          </div>
        </section>

        {/* 3. Button Component Library */}
        <section className="space-y-4">
          <h3 className="text-lg font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
            3. Controlled Button System (Immutable Specifications)
          </h3>
          <div className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="primary">Primary Action</Button>
              <Button variant="secondary">Secondary Action</Button>
              <Button variant="outline">Ghost / Outline</Button>
              <Button variant="danger">Destructive Action</Button>
              <Button variant="primary" isLoading>
                Loading
              </Button>
              <Button variant="primary" disabled>
                Disabled
              </Button>
            </div>
            <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-[#F0E4D2] dark:border-[#3D322A]">
              <Button variant="primary" size="compact">
                Compact (36px)
              </Button>
              <Button variant="primary" size="standard">
                Standard (40px)
              </Button>
              <Button variant="primary" size="mobile">
                Mobile Touch (44px)
              </Button>
            </div>
          </div>
        </section>

        {/* 4. Stat Cards & Confidence */}
        <section className="space-y-4">
          <h3 className="text-lg font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
            4. Stat Cards & Confidence Indicators
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Documents Analyzed"
              value={14}
              subtitle="Indexed on device"
              accentColor="#F4B860"
            />
            <StatCard
              title="Claims Extracted"
              value={128}
              subtitle="Across verified papers"
              accentColor="#39765B"
            />
            <StatCard
              title="Supported Claims"
              value={94}
              subtitle="73.4% empirical backing"
              accentColor="#39765B"
            />
            <StatCard
              title="Flagged Claims"
              value={34}
              subtitle="Requires human audit"
              tooltip="Includes unsupported, contradictory, and unverified claims"
              accentColor="#B94D4D"
            />
          </div>

          <div className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] flex flex-wrap items-center gap-8">
            <ConfidenceIndicator confidence={0.92} />
            <ConfidenceIndicator confidence={0.65} />
            <ConfidenceIndicator confidence={0.35} />
          </div>
        </section>

        {/* 5. Accessible Form Controls */}
        <section className="space-y-4">
          <h3 className="text-lg font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
            5. Accessible Form Controls
          </h3>
          <div className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input label="Document Title" placeholder="e.g. Attention Is All You Need" />
            <PasswordInput
              label="Password"
              value={testPassword}
              onChange={(e) => setTestPassword(e.target.value)}
              showStrengthChecklist
            />
            <Select
              label="Filter by Scholarly Provider"
              options={[
                { value: "all", label: "All Repositories (OpenAlex, Crossref, Europe PMC)" },
                { value: "openalex", label: "OpenAlex" },
                { value: "crossref", label: "Crossref" },
                { value: "europe_pmc", label: "Europe PMC" },
              ]}
            />
            <Checkbox
              label="I understand that retrieval failure does not imply claim falsity."
              description="CiteVerify marks unretrieved papers as UNABLE_TO_VERIFY instead of refuting them."
              checked={testCheckbox}
              onChange={(e) => setTestCheckbox(e.target.checked)}
            />
            <div className="md:col-span-2">
              <Textarea
                label="Reviewer Verification Notes"
                rows={2}
                placeholder="Document methodology findings or reasons for verdict adjustment..."
              />
            </div>
          </div>
        </section>

        {/* 6. Loading States */}
        <section className="space-y-4">
          <h3 className="text-lg font-bold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
            6. Loading States & Skeletons
          </h3>
          <div className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] flex items-center gap-6">
            <Spinner size="lg" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
