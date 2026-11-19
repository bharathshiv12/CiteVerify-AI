"use client";

import React, { useEffect } from "react";
import { Button } from "../components/ui/button";
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global React error boundary caught error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] flex flex-col items-center justify-center p-6 text-center text-[#3E2F27] dark:text-[#F3E9DD]">
      <div className="w-16 h-16 rounded-full bg-[#F6E1E1] dark:bg-[#B94D4D]/20 text-[#B94D4D] flex items-center justify-center mb-4">
        <AlertTriangle className="w-8 h-8" />
      </div>
      <h2 className="text-2xl font-extrabold font-heading text-[#8F2E2E] dark:text-[#fca5a5]">
        Application Error Encountered
      </h2>
      <p className="mt-2 text-xs sm:text-sm text-[#7A685D] dark:text-[#B8A898] max-w-md">
        {error.message || "An unexpected client exception interrupted the verification interface."}
      </p>
      {error.digest && (
        <p className="mt-2 text-[10px] font-mono text-[#A08B78] dark:text-[#8C7A6A]">
          Digest: {error.digest}
        </p>
      )}
      <div className="mt-6 flex items-center gap-3">
        <Button
          variant="primary"
          size="compact"
          onClick={() => reset()}
          leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
        >
          Recover View
        </Button>
      </div>
    </div>
  );
}
