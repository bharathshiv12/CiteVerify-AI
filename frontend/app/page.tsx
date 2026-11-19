"use client";

import { useEffect, useState } from "react";
import { checkHealth } from "../services/api";

export default function Home() {
  const [healthStatus, setHealthStatus] = useState<string>("Checking backend...");
  const useMocks = process.env.NEXT_PUBLIC_USE_MOCKS === "true";
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  useEffect(() => {
    checkHealth()
      .then((data) => setHealthStatus(`Online (${data.service} v${data.version})`))
      .catch(() => setHealthStatus("Backend Offline (Ensure FastAPI is running on port 8000)"));
  }, []);

  return (
    <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-10">
      {useMocks && (
        <div className="mb-6 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-700 dark:text-amber-300 text-sm font-semibold flex items-center justify-between">
          <span>⚠️ SAMPLE DATA MODE ACTIVE (Synthetic data fixtures loaded from contracts/examples/)</span>
          <span className="text-xs uppercase bg-amber-500/20 px-2 py-0.5 rounded">Mock</span>
        </div>
      )}

      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl text-slate-900 dark:text-white">
          Cite<span className="text-blue-600 dark:text-blue-400">Verify</span> AI
        </h1>
        <p className="mt-3 text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
          Scientific Claim and Citation Verification System.
        </p>
        <div className="mt-4 inline-block bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800 rounded-full px-4 py-1.5 text-xs text-blue-700 dark:text-blue-300 font-medium">
          <strong>Core Principle:</strong> A real citation does not automatically support its claim. We verify the claim against the evidence.
        </div>
      </header>

      {/* Backend Health Badge */}
      <div className="mb-8 flex items-center justify-center gap-2 text-xs text-slate-500">
        <span>Backend API ({apiBaseUrl}):</span>
        <span className={`px-2 py-0.5 rounded font-mono ${
          healthStatus.startsWith("Online")
            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
            : "bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
        }`}>
          {healthStatus}
        </span>
      </div>

      {/* Upload Box Placeholder for Agent 1 */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-8 shadow-sm text-center">
        <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-12 hover:border-blue-500 transition-colors">
          <svg className="mx-auto h-12 w-12 text-slate-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <p className="mt-4 text-sm font-medium text-slate-700 dark:text-slate-300">
            Upload an academic paper PDF to verify claims against cited sources
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Supported formats: PDF (up to 25MB). Multi-page text extraction and citation graph analysis.
          </p>
          <button className="mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm">
            Select PDF File
          </button>
        </div>
      </section>
    </main>
  );
}

