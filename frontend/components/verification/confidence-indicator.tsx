import React from "react";
import { HelpCircle } from "lucide-react";
import { getConfidenceTier, CONFIDENCE_CONFIG } from "../../lib/constants/verdicts";

interface ConfidenceIndicatorProps {
  confidence: number;
  showBar?: boolean;
  className?: string;
}

export function ConfidenceIndicator({
  confidence,
  showBar = true,
  className = "",
}: ConfidenceIndicatorProps) {
  const tier = getConfidenceTier(confidence);
  const config = CONFIDENCE_CONFIG[tier];
  const percent = Math.round(confidence * 100);

  return (
    <div className={`inline-flex flex-col gap-1 ${className}`}>
      <div className="flex items-center gap-1.5 text-xs font-semibold select-none">
        <span className={`px-2 py-0.5 rounded-full ${config.bgClass} ${config.textClass} border border-current/20 text-[11px]`}>
          {config.label} ({percent}%)
        </span>
        <span
          title={config.tooltip}
          className="cursor-help text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD]"
          aria-label={config.tooltip}
        >
          <HelpCircle className="w-3.5 h-3.5" />
        </span>
      </div>
      {showBar && (
        <div className="w-24 h-1.5 bg-[#F0E4D2] dark:bg-[#3D322A] rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              tier === "HIGH" ? "bg-[#39765B]" : tier === "MEDIUM" ? "bg-[#B68A42]" : "bg-[#B94D4D]"
            }`}
            style={{ width: `${percent}%` }}
          />
        </div>
      )}
    </div>
  );
}
