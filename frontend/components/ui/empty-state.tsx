import React from "react";
import { FolderSearch, AlertTriangle, ArrowRight } from "lucide-react";
import { Button } from "./button";

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-8 sm:p-12 text-center rounded-[14px] bg-white/60 dark:bg-[#2A221C]/60 border border-dashed border-[#F0E4D2] dark:border-[#3D322A] ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center mb-4">
        {icon || <FolderSearch className="w-6 h-6" />}
      </div>
      <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">{title}</h3>
      <p className="mt-1.5 text-xs text-[#7A685D] dark:text-[#B8A898] max-w-sm leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <div className="mt-5">
          <Button variant="primary" size="compact" onClick={onAction} rightIcon={<ArrowRight className="w-3.5 h-3.5" />}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
}

interface ErrorStateProps {
  title?: string;
  message: string;
  requestId?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Something went wrong",
  message,
  requestId,
  onRetry,
  className = "",
}: ErrorStateProps) {
  return (
    <div
      className={`p-6 rounded-[14px] bg-[#F6E1E1]/40 dark:bg-[#B94D4D]/10 border border-[#B94D4D]/30 text-center flex flex-col items-center ${className}`}
    >
      <div className="w-10 h-10 rounded-full bg-[#F6E1E1] dark:bg-[#B94D4D]/20 text-[#B94D4D] flex items-center justify-center mb-3">
        <AlertTriangle className="w-5 h-5" />
      </div>
      <h4 className="text-sm font-bold text-[#8F2E2E] dark:text-[#fca5a5]">{title}</h4>
      <p className="mt-1 text-xs text-[#8F2E2E]/80 dark:text-[#fca5a5]/80 max-w-md">{message}</p>
      {requestId && (
        <p className="mt-2 text-[10px] font-mono text-[#8F2E2E]/60 dark:text-[#fca5a5]/60">
          Request ID: {requestId}
        </p>
      )}
      {onRetry && (
        <div className="mt-4">
          <Button variant="outline" size="compact" onClick={onRetry}>
            Try Again
          </Button>
        </div>
      )}
    </div>
  );
}
