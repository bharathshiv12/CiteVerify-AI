"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "../../components/layout/app-shell";
import { FileUploader } from "../../components/verification/file-uploader";
import { Button } from "../../components/ui/button";
import { useUploadDocument, useStartAnalysis } from "../../hooks/use-document";
import { registerDocument } from "../../lib/document-registry";
import { useAuth } from "../../lib/supabase/auth-context";
import { ShieldCheck, FileText, ArrowRight, AlertTriangle } from "lucide-react";

export default function VerifyPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const uploadMutation = useUploadDocument();
  const startAnalysisMutation = useStartAnalysis();

  const handleStartVerification = async () => {
    if (!selectedFile) return;

    setUploadError(null);
    try {
      // 1. Upload PDF document
      const doc = await uploadMutation.mutateAsync(selectedFile);

      // 2. Register document in device storage
      registerDocument(
        {
          document_id: doc.id,
          filename: doc.filename,
          uploaded_at: doc.created_at || new Date().toISOString(),
          file_size_bytes: doc.file_size_bytes,
        },
        user?.id
      );

      // 3. Start background analysis
      await startAnalysisMutation.mutateAsync(doc.id);

      // 4. Navigate to stage 2 (Extract)
      router.push(`/verify/${doc.id}/extract`);
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : "Upload failed.");
    }
  };

  const isPending = uploadMutation.isPending || startAnalysisMutation.isPending;

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-8 pb-16">
        {/* Header */}
        <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] text-xs font-bold mb-3">
            <ShieldCheck className="w-3.5 h-3.5 text-[#39765B]" />
            Stage 01 of 06: Document Intake & Binary Validation
          </div>
          <h2 className="text-2xl font-extrabold font-heading text-[#3E2F27] dark:text-[#F3E9DD]">
            Verify Academic Document
          </h2>
          <p className="mt-1.5 text-xs sm:text-sm text-[#7A685D] dark:text-[#B8A898] max-w-2xl leading-relaxed">
            Upload a research publication PDF. CiteVerify will extract factual claims, detect in-text citations, resolve referenced papers in scholarly databases, and verify claim assertions against source evidence.
          </p>
        </div>

        {/* Upload Zone */}
        <div className="p-6 sm:p-8 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-6">
          <FileUploader
            onFileSelected={(file) => setSelectedFile(file)}
            isLoading={isPending}
          />

          {uploadError && (
            <div className="p-3.5 rounded-[10px] bg-[#F6E1E1] text-[#8F2E2E] dark:bg-[#B94D4D]/20 dark:text-[#fca5a5] text-xs font-medium flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-[#F0E4D2] dark:border-[#3D322A]">
            <p className="text-[11px] text-[#7A685D] dark:text-[#B8A898]">
              Format: Standard PDF (%PDF- header validated). Max file size: 25MB.
            </p>
            <Button
              variant="primary"
              size="standard"
              disabled={!selectedFile || isPending}
              isLoading={isPending}
              onClick={handleStartVerification}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Start Verification Pipeline
            </Button>
          </div>
        </div>

        {/* Informational Guidance */}
        <div className="p-5 rounded-[14px] bg-[#FFF0D6]/40 dark:bg-[#33291F]/40 border border-[#F0E4D2] dark:border-[#3D322A] text-xs text-[#7A685D] dark:text-[#B8A898] space-y-2">
          <div className="font-bold text-[#8D6E63] dark:text-[#D7B8A8] flex items-center gap-1.5">
            <FileText className="w-4 h-4" />
            Verification Pipeline Sequence
          </div>
          <ol className="list-decimal list-inside space-y-1 text-[11px] leading-relaxed">
            <li><strong>Intake & Validation:</strong> Magic byte check (%PDF-) and extension validation.</li>
            <li><strong>Claim Extraction:</strong> Sentence-level isolation of factual empirical statements.</li>
            <li><strong>Citation Parsing:</strong> Author-year and numeric citation marker detection.</li>
            <li><strong>Scholarly Retrieval:</strong> OpenAlex, Crossref, and Europe PMC querying.</li>
            <li><strong>Evidence Comparison:</strong> Semantic ranking and Natural Language Inference.</li>
            <li><strong>Report Synthesis:</strong> Traceable report with reliability score and audit history.</li>
          </ol>
        </div>
      </div>
    </AppShell>
  );
}
