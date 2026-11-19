"use client";

import React, { useEffect } from "react";
import { X } from "lucide-react";

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl";
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  maxWidth = "md",
}: ModalProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = "hidden";
      window.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      document.body.style.overflow = "unset";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const widthClass = {
    sm: "max-w-sm",
    md: "max-w-md",
    lg: "max-w-lg",
    xl: "max-w-xl",
    "2xl": "max-w-2xl",
  }[maxWidth];

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div
        className="fixed inset-0"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className={`relative w-full ${widthClass} bg-white dark:bg-[#2A221C] rounded-[14px] border border-[#F0E4D2] dark:border-[#3D322A] shadow-xl overflow-hidden z-10`}
      >
        {(title || description) && (
          <div className="flex items-start justify-between p-5 border-b border-[#F0E4D2] dark:border-[#3D322A]">
            <div>
              {title && (
                <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                  {title}
                </h3>
              )}
              {description && (
                <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
                  {description}
                </p>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD] hover:bg-[#FFF0D6]/40 dark:hover:bg-[#33291F] transition-colors"
              aria-label="Close dialog"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
        <div className="p-5">{children}</div>
      </div>
    </div>
  );
}
