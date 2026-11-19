import React from "react";
import { Check } from "lucide-react";

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: React.ReactNode;
  description?: string;
}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, description, className = "", id, checked, ...props }, ref) => {
    const inputId = id || (typeof label === "string" ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className={`flex items-start gap-2.5 ${className}`}>
        <div className="relative flex items-center justify-center mt-0.5">
          <input
            id={inputId}
            ref={ref}
            type="checkbox"
            checked={checked}
            className="peer sr-only"
            {...props}
          />
          <div className="w-4 h-4 rounded-[4px] border border-[#A08B78] dark:border-[#8C7A6A] bg-white dark:bg-[#2A221C] peer-checked:bg-[#F4B860] peer-checked:border-[#F4B860] peer-focus-visible:ring-2 peer-focus-visible:ring-[#8D6E63] transition-colors flex items-center justify-center cursor-pointer">
            <Check className="w-3 h-3 text-[#3E2F27] opacity-0 peer-checked:opacity-100 transition-opacity stroke-[3]" />
          </div>
        </div>
        {(label || description) && (
          <label htmlFor={inputId} className="text-xs text-[#3E2F27] dark:text-[#F3E9DD] cursor-pointer select-none">
            {label && <span className="font-medium">{label}</span>}
            {description && <p className="text-[11px] text-[#7A685D] dark:text-[#B8A898] mt-0.5">{description}</p>}
          </label>
        )}
      </div>
    );
  }
);

Checkbox.displayName = "Checkbox";
