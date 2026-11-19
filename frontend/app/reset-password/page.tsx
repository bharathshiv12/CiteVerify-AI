"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Logo } from "../../components/brand/logo";
import { PasswordInput } from "../../components/ui/password-input";
import { Button } from "../../components/ui/button";
import { useAuth } from "../../lib/supabase/auth-context";
import { getSupabaseClient } from "../../lib/supabase/client";
import { CheckCircle2 } from "lucide-react";

export default function ResetPasswordPage() {
  const router = useRouter();
  const { isConfigured } = useAuth();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Field validation checks for button enabling
  const isPasswordValid =
    newPassword.length >= 8 &&
    /[A-Z]/.test(newPassword) &&
    /[a-z]/.test(newPassword) &&
    /[0-9]/.test(newPassword);
  const isPasswordMatch = newPassword.length > 0 && newPassword === confirmPassword;
  const isFormValid = isPasswordValid && isPasswordMatch;
  const isSubmitDisabled = !isConfigured || isLoading || !isFormValid;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters in length.");
      return;
    }

    if (!/[A-Z]/.test(newPassword) || !/[a-z]/.test(newPassword) || !/[0-9]/.test(newPassword)) {
      setError("Password must contain at least one uppercase letter, one lowercase letter, and one number.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match. Please re-enter matching passwords.");
      return;
    }

    if (!isConfigured) {
      setError("Authentication service is currently unavailable. Supabase environment credentials are not configured.");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError("Authentication service is not configured. Please contact the administrator.");
      return;
    }

    setIsLoading(true);

    const { error: updateError } = await supabase.auth.updateUser({
      password: newPassword,
    });

    setIsLoading(false);
    if (updateError) {
      setError(updateError.message);
    } else {
      setSuccess(true);
    }
  };

  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-[#3E2F27] dark:text-[#F3E9DD]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Logo size="lg" withLink={false} />
        <h2 className="mt-6 text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
          Set New Password
        </h2>
        <p className="mt-2 text-xs text-[#7A685D] dark:text-[#B8A898]">
          Enter and confirm your new secure academic account password
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white dark:bg-[#2A221C] py-8 px-6 shadow-brand rounded-[16px] border border-[#F0E4D2] dark:border-[#3D322A] sm:px-10">
          {success ? (
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-[#E4F1EA] text-[#39765B] flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">Password Updated</h3>
              <p className="text-xs text-[#7A685D] dark:text-[#B8A898]">
                Your password has been successfully updated. You may now sign in with your new credentials.
              </p>
              <div className="pt-4">
                <Button
                  variant="primary"
                  size="compact"
                  onClick={() => router.push("/login")}
                  className="w-full"
                >
                  Proceed to Sign In
                </Button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <PasswordInput
                label="New Password"
                required
                autoComplete="new-password"
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  if (error) setError(null);
                }}
                showStrengthChecklist
                placeholder="••••••••"
                disabled={isLoading}
              />

              <PasswordInput
                label="Confirm New Password"
                required
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="••••••••"
                disabled={isLoading}
              />

              {error && (
                <div className="p-3 rounded-[10px] bg-[#F6E1E1] text-[#8F2E2E] dark:bg-[#B94D4D]/20 dark:text-[#fca5a5] text-xs font-medium">
                  {error}
                </div>
              )}

              <div>
                <Button
                  type="submit"
                  variant="primary"
                  size="standard"
                  className="w-full"
                  isLoading={isLoading}
                  disabled={isSubmitDisabled}
                >
                  Update Password
                </Button>

                {!isConfigured && (
                  <p className="text-center text-[11px] text-[#A08B78] dark:text-[#8C7A6A] pt-2">
                    Supabase authentication pending configuration in <code className="font-mono text-[10px]">.env.local</code> (submission disabled)
                  </p>
                )}
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
