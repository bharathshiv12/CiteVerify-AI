"use client";

import React from "react";
import { Modal } from "./modal";
import { Button } from "./button";
import { AlertTriangle } from "lucide-react";

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "primary";
  isLoading?: boolean;
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  variant = "primary",
  isLoading = false,
}: ConfirmDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} maxWidth="sm">
      <div className="flex flex-col items-center text-center p-2">
        <div className="w-11 h-11 rounded-full bg-[#F6E1E1] dark:bg-[#B94D4D]/20 text-[#B94D4D] flex items-center justify-center mb-3">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <h4 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">{title}</h4>
        <p className="mt-2 text-xs text-[#7A685D] dark:text-[#B8A898] leading-relaxed">{message}</p>
        <div className="mt-6 flex items-center justify-center gap-3 w-full">
          <Button variant="outline" size="compact" onClick={onClose} disabled={isLoading} className="flex-1">
            {cancelLabel}
          </Button>
          <Button
            variant={variant === "danger" ? "danger" : "primary"}
            size="compact"
            onClick={onConfirm}
            isLoading={isLoading}
            className="flex-1"
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
