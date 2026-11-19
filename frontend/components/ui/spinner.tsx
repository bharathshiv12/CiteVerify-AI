import React from "react";
import { Loader2 } from "lucide-react";

export function Spinner({ size = "md", className = "" }: { size?: "sm" | "md" | "lg"; className?: string }) {
  const sizeMap = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };
  return (
    <Loader2
      className={`animate-spin text-[#F4B860] ${sizeMap[size]} ${className}`}
      aria-label="Loading..."
    />
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse bg-[#F0E4D2]/60 dark:bg-[#3D322A]/60 rounded-[8px] ${className}`}
      aria-hidden="true"
    />
  );
}
