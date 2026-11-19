import React from "react";
import { HelpCircle } from "lucide-react";

interface StatCardProps {
  title: string;
  value: number | string;
  icon?: React.ReactNode;
  subtitle?: string;
  tooltip?: string;
  accentColor?: string;
  className?: string;
}

export function StatCard({
  title,
  value,
  icon,
  subtitle,
  tooltip,
  accentColor,
  className = "",
}: StatCardProps) {
  return (
    <div
      className={`relative p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand overflow-hidden flex flex-col justify-between ${className}`}
    >
      {accentColor && (
        <div
          className="absolute top-0 left-0 right-0 h-1"
          style={{ backgroundColor: accentColor }}
        />
      )}
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#7A685D] dark:text-[#B8A898] flex items-center gap-1.5">
          {title}
          {tooltip && (
            <span title={tooltip} className="cursor-help text-[#A08B78] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD]">
              <HelpCircle className="w-3.5 h-3.5" />
            </span>
          )}
        </span>
        {icon && <div className="text-[#8D6E63] dark:text-[#D7B8A8] opacity-80">{icon}</div>}
      </div>
      <div className="mt-3">
        <div className="text-2xl sm:text-3xl font-extrabold font-heading text-[#3E2F27] dark:text-[#F3E9DD] tabular-nums tracking-tight">
          {value}
        </div>
        {subtitle && (
          <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">{subtitle}</p>
        )}
      </div>
    </div>
  );
}
