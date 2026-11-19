"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Logo } from "../../components/brand/logo";
import { Input } from "../../components/ui/input";
import { PasswordInput } from "../../components/ui/password-input";
import { Button } from "../../components/ui/button";
import { Checkbox } from "../../components/ui/checkbox";
import { useAuth } from "../../lib/supabase/auth-context";
import { getSupabaseClient } from "../../lib/supabase/client";
import { AlertCircle, CheckCircle2, ArrowRight } from "lucide-react";

export default function SignupPage() {
  const router = useRouter();
  const { isConfigured } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [institution, setInstitution] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isConfigured) {
      router.push("/dashboard");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (!acceptTerms) {
      setError("Please accept the Terms of Service and Privacy Policy.");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) return;

    setIsLoading(true);
    setError(null);

    const { error: signUpError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName.trim(),
          institution: institution.trim(),
        },
      },
    });

    setIsLoading(false);
    if (signUpError) {
      setError(signUpError.message);
    } else {
      setSuccessMessage("Account created! Check your email to confirm your account, or sign in now.");
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
          {!isConfigured && (
            <div className="mb-6 p-3.5 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] border border-[#F4B860]/40 text-xs space-y-1 text-[#3E2F27] dark:text-[#F3E9DD]">
              <div className="flex items-center gap-1.5 font-bold text-[#8D6E63] dark:text-[#D7B8A8]">
                <AlertCircle className="w-4 h-4 text-[#B77B35]" />
                Authentication is not configured.
              </div>
              <p className="text-[11px] text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
                Supabase credentials are not configured. You can proceed directly to the workspace as a guest.
              </p>
              <div className="pt-2">
                <Button
                  type="button"
                  variant="primary"
                  size="compact"
                  onClick={() => router.push("/dashboard")}
                  className="w-full"
                  rightIcon={<ArrowRight className="w-3.5 h-3.5" />}
                >
                  Continue to Workspace as Guest
                </Button>
              </div>
            </div>
          )}

          {successMessage ? (
            <div className="p-4 rounded-[12px] bg-[#E4F1EA] text-[#1F5A42] text-xs space-y-2 text-center">
              <CheckCircle2 className="w-8 h-8 text-[#39765B] mx-auto" />
              <p className="font-bold text-sm">Registration Successful</p>
              <p>{successMessage}</p>
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
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Jane Smith"
                disabled={!isConfigured}
              />

              <Input
                label="Institution or University"
                required
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
                placeholder="Stanford University / Oxford"
                disabled={!isConfigured}
              />

              <Input
                label="Academic Email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane.smith@stanford.edu"
                disabled={!isConfigured}
              />

              <PasswordInput
                label="Create Password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                showStrengthChecklist
                placeholder="••••••••"
                disabled={!isConfigured}
              />

              <PasswordInput
                label="Confirm Password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                disabled={!isConfigured}
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
                disabled={!isConfigured}
              />

              {error && (
                <div className="p-3 rounded-[10px] bg-[#F6E1E1] text-[#8F2E2E] dark:bg-[#B94D4D]/20 dark:text-[#fca5a5] text-xs font-medium">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="standard"
                className="w-full"
                isLoading={isLoading}
                disabled={!isConfigured}
              >
                Create Account
              </Button>
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
