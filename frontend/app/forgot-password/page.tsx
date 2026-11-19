"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Logo } from "../../components/brand/logo";
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";
import { useAuth } from "../../lib/supabase/auth-context";
import { getSupabaseClient } from "../../lib/supabase/client";
import { MailCheck, ArrowLeft } from "lucide-react";

export default function ForgotPasswordPage() {
  const { isConfigured } = useAuth();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Field validation checks for button enabling
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isFormValid = emailRegex.test(email.trim());
  const isSubmitDisabled = !isConfigured || isLoading || !isFormValid;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!isConfigured) {
      setError(
        "Authentication service is currently unavailable. Supabase environment credentials are not configured."
      );
      return;
    }

    if (!email.trim()) {
      setError("Please provide your registered academic email address.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("Please enter a valid academic email address (e.g. researcher@university.edu).");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError("Authentication service is unavailable.");
      return;
    }

    setIsLoading(true);
    const { error: resetError } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`,
    });
    setIsLoading(false);

    if (resetError) {
      setError(resetError.message);
    } else {
      setIsSubmitted(true);
    }
  };

  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-[#3E2F27] dark:text-[#F3E9DD]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Logo size="lg" withLink={false} />
        <h2 className="mt-6 text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
          Reset Password
        </h2>
        <p className="mt-2 text-xs text-[#7A685D] dark:text-[#B8A898]">
          Enter your academic email address to receive password recovery instructions
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white dark:bg-[#2A221C] py-8 px-6 shadow-brand rounded-[16px] border border-[#F0E4D2] dark:border-[#3D322A] sm:px-10">
          {isSubmitted ? (
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-[#E4F1EA] text-[#39765B] flex items-center justify-center mx-auto">
                <MailCheck className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-[#3E2F27] dark:text-[#F3E9DD]">Check your inbox</h3>
              <p className="text-xs text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
                If an account exists for that email, a reset link has been sent. Follow the instructions to choose a new password.
              </p>
              <div className="pt-4">
                <Link href="/login">
                  <Button variant="outline" size="compact" className="w-full">
                    Return to Sign In
                  </Button>
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="p-3 rounded-[10px] bg-[#F6E1E1] text-[#8F2E2E] dark:bg-[#B94D4D]/20 dark:text-[#fca5a5] text-xs font-medium">
                  {error}
                </div>
              )}

              <Input
                label="Registered Email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="researcher@university.edu"
                disabled={isLoading}
              />

              <div>
                <Button
                  type="submit"
                  variant="primary"
                  size="standard"
                  className="w-full"
                  isLoading={isLoading}
                  disabled={isSubmitDisabled}
                >
                  Send Reset Link
                </Button>

                {!isConfigured && (
                  <p className="text-center text-[11px] text-[#A08B78] dark:text-[#8C7A6A] pt-2">
                    Supabase authentication pending configuration in <code className="font-mono text-[10px]">.env.local</code> (submission disabled)
                  </p>
                )}
              </div>

              <div className="text-center pt-2">
                <Link
                  href="/login"
                  className="inline-flex items-center gap-1.5 text-xs text-[#8D6E63] dark:text-[#D7B8A8] font-semibold hover:underline"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back to Sign In
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
