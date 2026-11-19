import React from "react";
import { Check } from "lucide-react";

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: React.ReactNode;
  description?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, description, className = "", id, checked, disabled, ...props }, ref) => {
    const defaultId = React.useId();
    const inputId = id || defaultId;

    return (
      <div className={`flex items-start gap-2.5 ${disabled ? "opacity-60 cursor-not-allowed" : ""} ${className}`}>
        <div className="relative flex items-center justify-center mt-0.5">
          <input
            id={inputId}
            ref={ref}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            className="peer sr-only"
            {...props}
          />
          <label
            htmlFor={inputId}
            className={`w-4 h-4 rounded-[4px] border border-[#A08B78] dark:border-[#8C7A6A] bg-white dark:bg-[#2A221C] peer-checked:bg-[#F4B860] peer-checked:border-[#F4B860] peer-focus-visible:ring-2 peer-focus-visible:ring-[#8D6E63] transition-colors flex items-center justify-center ${
              disabled ? "cursor-not-allowed" : "cursor-pointer"
            }`}
          >
            <Check className="w-3 h-3 text-[#3E2F27] opacity-0 peer-checked:opacity-100 transition-opacity stroke-[3] pointer-events-none" />
          </label>
        </div>
        {(label || description) && (
          <div className="text-xs text-[#3E2F27] dark:text-[#F3E9DD] select-none">
            {label && (
              <label
                htmlFor={inputId}
                className={`${disabled ? "cursor-not-allowed" : "cursor-pointer"} font-medium`}
              >
                {label}
              </label>
            )}
            {description && <p className="text-[11px] text-[#7A685D] dark:text-[#B8A898] mt-0.5">{description}</p>}
          </div>
        )}
      </div>
    );
  }
);

Checkbox.displayName = "Checkbox";
