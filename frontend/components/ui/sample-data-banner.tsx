"use client";

import React from "react";
import { AlertCircle } from "lucide-react";
import { USE_MOCKS } from "../../services/api";

export function SampleDataBanner() {
  if (!USE_MOCKS) return null;

  return (
    <div
      role="alert"
      className="banner-sample w-full bg-[#FFF0D6] dark:bg-[#33291F] border-b border-[#F4B860] px-4 py-2 text-xs font-medium text-[#3E2F27] dark:text-[#F3E9DD] flex items-center justify-between gap-3 select-none"
    >
      <div className="flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-[#B77B35] flex-shrink-0" aria-hidden="true" />
        <span>
          <strong>SAMPLE DATA MODE ACTIVE:</strong> Synthetic fixtures loaded from{" "}
          <code className="font-mono bg-[#FFDCA8] dark:bg-[#4A3A28] px-1 py-0.5 rounded text-[11px]">
            contracts/examples/
          </code>
          . Responses do not represent live scientific verification.
        </span>
      </div>
      <span className="flex-shrink-0 text-[10px] font-bold uppercase tracking-wider bg-[#F4B860] text-[#3E2F27] px-2 py-0.5 rounded">
        Mock Mode
      </span>
    </div>
  );
}
