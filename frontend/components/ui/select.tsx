import React from "react";
import { ChevronDown } from "lucide-react";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  hint?: string;
  options?: { value: string; label: string }[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, hint, options, children, className = "", id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-xs font-semibold text-[#3E2F27] dark:text-[#F3E9DD] mb-1.5">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <div className="relative flex items-center">
          <select
            id={inputId}
            ref={ref}
            className={`w-full h-[40px] pl-3.5 pr-9 text-sm rounded-[10px] bg-white dark:bg-[#2A221C] text-[#3E2F27] dark:text-[#F3E9DD] border appearance-none ${
              error
                ? "border-red-500 focus:ring-2 focus:ring-red-400"
                : "border-[#A08B78] dark:border-[#8C7A6A] focus:border-[#8D6E63] focus:ring-2 focus:ring-[#8D6E63]/20"
            } focus:outline-none transition-colors cursor-pointer ${className}`}
            {...props}
          >
            {options
              ? options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))
              : children}
          </select>
          <ChevronDown className="absolute right-3 w-4 h-4 text-[#7A685D] dark:text-[#B8A898] pointer-events-none" />
        </div>
        {error && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{error}</p>}
        {hint && !error && <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">{hint}</p>}
      </div>
    );
  }
);

Select.displayName = "Select";
