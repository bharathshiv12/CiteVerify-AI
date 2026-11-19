import React from "react";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "compact" | "standard" | "mobile";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = "primary",
      size = "standard",
      isLoading = false,
      disabled = false,
      leftIcon,
      rightIcon,
      className = "",
      ...props
    },
    ref
  ) => {
    // Exact locked button specifications from Section 4.6
    const baseClasses =
      "inline-flex items-center justify-center font-medium select-none transition-all duration-150 rounded-[10px] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#8D6E63] disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none active:scale-[0.98]";

    const sizeClasses = {
      compact: "h-[36px] px-3.5 text-xs gap-1.5",
      standard: "h-[40px] px-4 text-sm gap-2",
      mobile: "h-[44px] px-5 text-base gap-2.5",
    }[size];

    const variantClasses = {
      // Primary: #F4B860 bg, #3E2F27 text, no gradient, no white text
      primary: "bg-[#F4B860] hover:bg-[#eab057] text-[#3E2F27] border border-transparent shadow-sm",
      // Secondary: #FFDCA8 bg, #3E2F27 text, no gradient
      secondary: "bg-[#FFDCA8] hover:bg-[#f6d19a] text-[#3E2F27] border border-transparent",
      // Ghost / Outline: Border #A08B78, #3E2F27 text
      outline:
        "bg-transparent hover:bg-[#FFF0D6]/50 dark:hover:bg-[#33291F] text-[#3E2F27] dark:text-[#F3E9DD] border border-[#A08B78] dark:border-[#8C7A6A]",
      ghost:
        "bg-transparent hover:bg-[#FFF0D6]/60 dark:hover:bg-[#33291F] text-[#3E2F27] dark:text-[#F3E9DD] border border-transparent",
      danger:
        "bg-[#F6E1E1] hover:bg-[#edd4d4] text-[#8F2E2E] dark:bg-[#B94D4D]/20 dark:text-[#fca5a5] border border-[#B94D4D]/30",
    }[variant];

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`${baseClasses} ${sizeClasses} ${variantClasses} ${className}`}
        {...props}
      >
        {isLoading && <Loader2 className="w-4 h-4 animate-spin text-[#3E2F27] dark:text-current" />}
        {!isLoading && leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
        <span>{children}</span>
        {!isLoading && rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = "Button";
