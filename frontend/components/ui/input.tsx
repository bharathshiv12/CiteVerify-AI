import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, leftIcon, rightIcon, className = "", id, ...props }, ref) => {
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
          {leftIcon && (
            <div className="absolute left-3.5 text-[#7A685D] dark:text-[#B8A898] pointer-events-none">
              {leftIcon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            className={`w-full h-[40px] px-3.5 text-sm rounded-[10px] bg-white dark:bg-[#2A221C] text-[#3E2F27] dark:text-[#F3E9DD] placeholder-[#7A685D]/60 dark:placeholder-[#B8A898]/40 border ${
              error
                ? "border-red-500 focus:ring-2 focus:ring-red-400"
                : "border-[#A08B78] dark:border-[#8C7A6A] focus:border-[#8D6E63] focus:ring-2 focus:ring-[#8D6E63]/20"
            } ${leftIcon ? "pl-10" : ""} ${rightIcon ? "pr-10" : ""} focus:outline-none transition-colors ${className}`}
            {...props}
          />
          {rightIcon && <div className="absolute right-3.5 text-[#7A685D] dark:text-[#B8A898]">{rightIcon}</div>}
        </div>
        {error && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{error}</p>}
        {hint && !error && <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">{hint}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
