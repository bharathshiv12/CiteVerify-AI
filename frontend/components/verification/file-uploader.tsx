"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, X, RefreshCw } from "lucide-react";
import { Button } from "../ui/button";

interface FileUploaderProps {
  onFileSelected: (file: File) => void;
  isLoading?: boolean;
  maxSizeMB?: number;
}

export function FileUploader({
  onFileSelected,
  isLoading = false,
  maxSizeMB = Number(process.env.NEXT_PUBLIC_MAX_UPLOAD_MB) || 25,
}: FileUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndSetFile = (file: File) => {
    setError(null);

    // 1. Extension check (.pdf)
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Invalid file format. Only academic PDF documents (.pdf) are accepted.");
      return;
    }

    // 2. MIME type check
    if (file.type && file.type !== "application/pdf") {
      setError("Invalid MIME type. Expected application/pdf.");
      return;
    }

    // 3. Empty file check
    if (file.size === 0) {
      setError("The selected file is empty (0 bytes). Please select a valid research document.");
      return;
    }

    // 4. File size limit
    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      setError(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds maximum limit of ${maxSizeMB}MB.`);
      return;
    }

    setSelectedFile(file);
    onFileSelected(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleManualChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf,.pdf"
        className="hidden"
        onChange={handleManualChange}
        disabled={isLoading}
      />

      {!selectedFile ? (
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative flex flex-col items-center justify-center p-8 sm:p-12 border-2 border-dashed rounded-[14px] cursor-pointer transition-all ${
            dragActive
              ? "border-[#F4B860] bg-[#FFF0D6]/40 dark:bg-[#33291F]/40"
              : "border-[#A08B78]/50 dark:border-[#8C7A6A]/50 hover:border-[#8D6E63] bg-white/70 dark:bg-[#2A221C]/70"
          }`}
        >
          <div className="w-14 h-14 rounded-full bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center mb-4">
            <UploadCloud className="w-7 h-7" />
          </div>

          <p className="text-sm sm:text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD] text-center">
            Drop your research document here, or <span className="text-[#8D6E63] dark:text-[#D7B8A8] underline">browse</span>
          </p>
          <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898] text-center">
            Accepts academic papers in PDF format up to {maxSizeMB}MB
          </p>

          <div className="mt-5">
            <Button
              type="button"
              variant="secondary"
              size="compact"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
            >
              Browse Files
            </Button>
          </div>
        </div>
      ) : (
        /* Selected file preview card */
        <div className="p-5 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand flex items-center justify-between gap-4">
          <div className="flex items-center gap-3.5 min-w-0">
            <div className="w-11 h-11 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center flex-shrink-0">
              <FileText className="w-6 h-6" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-bold text-[#3E2F27] dark:text-[#F3E9DD] truncate">
                {selectedFile.name}
              </p>
              <div className="flex items-center gap-2 text-xs text-[#7A685D] dark:text-[#B8A898] mt-0.5">
                <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
                <span>•</span>
                <span className="text-emerald-700 dark:text-emerald-400 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Ready for verification
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <Button
              type="button"
              variant="outline"
              size="compact"
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
            >
              Replace
            </Button>
            <button
              type="button"
              onClick={handleRemove}
              disabled={isLoading}
              className="p-2 rounded-lg text-[#7A685D] hover:text-red-600 dark:hover:text-red-400 hover:bg-[#F6E1E1]/40 transition-colors"
              aria-label="Remove selected file"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="p-3 rounded-[10px] bg-[#F6E1E1] dark:bg-[#B94D4D]/20 text-[#8F2E2E] dark:text-[#fca5a5] text-xs font-medium flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
