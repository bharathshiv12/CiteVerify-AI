"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Logo } from "../../components/brand/logo";
import { Input } from "../../components/ui/input";
import { PasswordInput } from "../../components/ui/password-input";
import { Button } from "../../components/ui/button";
import { Checkbox } from "../../components/ui/checkbox";
import { useAuth } from "../../lib/supabase/auth-context";
import { getSupabaseClient } from "../../lib/supabase/client";
import { AlertCircle, CheckCircle2, Mail } from "lucide-react";

export default function SignupPage() {
  const router = useRouter();
  const { user, isConfigured, isLoading: authLoading } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [institution, setInstitution] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [registeredEmail, setRegisteredEmail] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Field validation checks for button enabling
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isPasswordStrengthValid =
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password);
  const isPasswordMatch = password.length > 0 && password === confirmPassword;
  const isEmailValid = emailRegex.test(email.trim());
  const isFullNameValid = fullName.trim().length > 0;
  const isInstitutionValid = institution.trim().length > 0;

  const isFormValid =
    isFullNameValid &&
    isInstitutionValid &&
    isEmailValid &&
    isPasswordStrengthValid &&
    isPasswordMatch &&
    acceptTerms;

  const isSubmitDisabled = !isConfigured || isLoading || !isFormValid;

  // If already authenticated, redirect to workspace
  useEffect(() => {
    if (!authLoading && user) {
      router.push("/dashboard");
    }
  }, [authLoading, user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!isConfigured) {
      setError(
        "Authentication service is not configured. Supabase credentials must be defined in .env.local."
      );
      return;
    }

    if (!fullName.trim()) {
      setError("Please provide your full academic name or title.");
      return;
    }

    if (!institution.trim()) {
      setError("Please specify your associated research institution or university.");
      return;
    }

    if (!email.trim()) {
      setError("Please provide a valid academic email address.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("Please provide a valid academic email address (e.g. researcher@university.edu).");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters in length.");
      return;
    }

    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
      setError("Password must contain at least one uppercase letter, one lowercase letter, and one number.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match. Please re-enter your password confirmation.");
      return;
    }

    if (!acceptTerms) {
      setError("You must accept the Terms of Service and Privacy Policy to create an account.");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError("Failed to initialize authentication client.");
      return;
    }

    setIsLoading(true);

    try {
      const { data, error: signUpError } = await supabase.auth.signUp({
        email: email.trim(),
        password,
        options: {
          data: {
            full_name: fullName.trim(),
            institution: institution.trim(),
          },
          emailRedirectTo:
            typeof window !== "undefined"
              ? `${window.location.origin}/auth/callback`
              : undefined,
        },
      });

      if (signUpError) {
        setError(signUpError.message);
        setIsLoading(false);
        return;
      }

      // If email confirmation is required, user exists but session may be null
      if (data.user) {
        setRegisteredEmail(email.trim());
      }
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while communicating with the authentication provider."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] flex flex-col justify-center py-12 sm:px-6 lg:px-8 text-[#3E2F27] dark:text-[#F3E9DD]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Logo size="lg" withLink={false} />
        <h2 className="mt-6 text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
          Create Research Account
        </h2>
        <p className="mt-2 text-xs text-[#7A685D] dark:text-[#B8A898]">
          Join academic reviewers verifying scientific literature integrity
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white dark:bg-[#2A221C] py-8 px-6 shadow-brand rounded-[16px] border border-[#F0E4D2] dark:border-[#3D322A] sm:px-10">
          {registeredEmail ? (
            <div className="p-5 rounded-[14px] bg-[#E4F1EA] dark:bg-[#1E3A2E] text-[#1F5A42] dark:text-[#6EE7B7] text-xs space-y-3 text-center border border-[#39765B]/20">
              <div className="w-12 h-12 rounded-full bg-white dark:bg-[#2A221C] text-[#39765B] flex items-center justify-center mx-auto shadow-sm">
                <Mail className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-base text-[#1F5A42] dark:text-[#6EE7B7]">
                Verification Email Dispatched
              </h3>
              <p className="text-xs leading-relaxed text-[#1F5A42]/90 dark:text-[#6EE7B7]/90">
                A confirmation link has been sent to <strong className="font-mono font-semibold">{registeredEmail}</strong>. Please check your academic email inbox and confirm your address to activate your account.
              </p>
              <div className="pt-2">
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
              <Input
                label="Full Name"
                required
                autoComplete="name"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="Dr. Jane Smith"
                disabled={isLoading}
              />

              <Input
                label="Institution or University"
                required
                value={institution}
                onChange={(e) => {
                  setInstitution(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="Stanford University / Oxford"
                disabled={isLoading}
              />

              <Input
                label="Academic Email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="jane.smith@stanford.edu"
                disabled={isLoading}
              />

              <PasswordInput
                label="Create Password"
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (error) setError(null);
                }}
                showStrengthChecklist
                placeholder="••••••••"
                disabled={isLoading}
              />

              <PasswordInput
                label="Confirm Password"
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

              <Checkbox
                label={
                  <span>
                    I accept the{" "}
                    <Link href="/terms" className="underline font-semibold" target="_blank">
                      Terms
                    </Link>{" "}
                    and{" "}
                    <Link href="/privacy" className="underline font-semibold" target="_blank">
                      Privacy Policy
                    </Link>
                  </span>
                }
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                disabled={isLoading}
              />

              {error && (
                <div className="p-3.5 rounded-[10px] bg-[#F6E1E1] text-[#8F2E2E] dark:bg-[#B94D4D]/20 dark:text-[#fca5a5] text-xs font-medium flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>{error}</span>
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
                  Create Academic Account
                </Button>

                {!isConfigured && (
                  <p className="text-center text-[11px] text-[#A08B78] dark:text-[#8C7A6A] pt-2">
                    Supabase authentication pending configuration in <code className="font-mono text-[10px]">.env.local</code> (submission disabled)
                  </p>
                )}
              </div>
            </form>
          )}

          <div className="mt-6 text-center text-xs text-[#7A685D] dark:text-[#B8A898] border-t border-[#F0E4D2] dark:border-[#3D322A] pt-4">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-bold text-[#8D6E63] dark:text-[#D7B8A8] hover:underline"
            >
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
