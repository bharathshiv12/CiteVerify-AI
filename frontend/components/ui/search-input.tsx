import React from "react";
import { Search, X } from "lucide-react";

interface SearchInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange"> {
  value: string;
  onChange: (value: string) => void;
  onClear?: () => void;
  placeholder?: string;
  className?: string;
}

export function SearchInput({
  value,
  onChange,
  onClear,
  placeholder = "Search...",
  className = "",
  ...props
}: SearchInputProps) {
  return (
    <div className={`relative flex items-center ${className}`}>
      <Search className="absolute left-3 w-4 h-4 text-[#7A685D] dark:text-[#B8A898] pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full h-[38px] pl-9 pr-8 text-sm rounded-[10px] bg-white dark:bg-[#2A221C] text-[#3E2F27] dark:text-[#F3E9DD] placeholder-[#7A685D]/60 dark:placeholder-[#B8A898]/40 border border-[#A08B78]/70 dark:border-[#8C7A6A] focus:border-[#8D6E63] focus:ring-2 focus:ring-[#8D6E63]/20 focus:outline-none transition-colors"
        {...props}
      />
      {value && (
        <button
          type="button"
          onClick={() => {
            onChange("");
            onClear?.();
          }}
          className="absolute right-2.5 p-0.5 text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD]"
          aria-label="Clear search"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
