"use client";

import React, { useState } from "react";
import { Eye, EyeOff, Lock } from "lucide-react";
import { Input, InputProps } from "./input";

export interface PasswordInputProps extends Omit<InputProps, "type" | "rightIcon"> {
  showStrengthChecklist?: boolean;
}

export function PasswordInput({
  label = "Password",
  value,
  showStrengthChecklist = false,
  ...props
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false);
  const passwordStr = String(value || "");

  const rules = [
    { label: "At least 8 characters", met: passwordStr.length >= 8 },
    { label: "At least one uppercase letter", met: /[A-Z]/.test(passwordStr) },
    { label: "At least one lowercase letter", met: /[a-z]/.test(passwordStr) },
    { label: "At least one number", met: /[0-9]/.test(passwordStr) },
  ];

  return (
    <div className="w-full">
      <Input
        label={label}
        type={showPassword ? "text" : "password"}
        value={value}
        leftIcon={<Lock className="w-4 h-4" />}
        rightIcon={
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="p-1 text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD] focus:outline-none"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        }
        {...props}
      />
      {showStrengthChecklist && passwordStr.length > 0 && (
        <div className="mt-2 space-y-1 p-2.5 bg-[#FFF0D6]/40 dark:bg-[#33291F]/40 border border-[#F0E4D2] dark:border-[#3D322A] rounded-lg">
          <p className="text-[11px] font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">Password requirements:</p>
          <ul className="text-xs space-y-0.5">
            {rules.map((r, i) => (
              <li
                key={i}
                className={`flex items-center gap-1.5 text-[11px] ${
                  r.met ? "text-emerald-700 dark:text-emerald-400 font-medium" : "text-[#7A685D] dark:text-[#B8A898]"
                }`}
              >
                <span>{r.met ? "✓" : "○"}</span>
                <span>{r.label}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
