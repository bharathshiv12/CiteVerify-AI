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
import { AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { user, isConfigured, isLoading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Field validation checks for button enabling
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isEmailValid = emailRegex.test(email.trim());
  const isPasswordPresent = password.length > 0;
  const isFormValid = isEmailValid && isPasswordPresent;
  const isSubmitDisabled = !isConfigured || isLoading || !isFormValid;

  // If already authenticated, redirect to workspace
  useEffect(() => {
    if (!authLoading && user) {
      router.push("/dashboard");
    }
  }, [authLoading, user, router]);

  // Check for session expired redirect query
  useEffect(() => {
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      if (params.get("expired") === "true") {
        setError("Your session has expired. Please authenticate to continue.");
      }
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!isConfigured) {
      setError(
        "Authentication service is currently unavailable. Supabase environment credentials are not configured on this deployment."
      );
      return;
    }

    if (!email.trim() || !password) {
      setError("Please provide both an academic email address and password.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError("Please enter a valid academic email address (e.g. researcher@university.edu).");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError("Failed to initialize authentication client.");
      return;
    }

    setIsLoading(true);

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });

      if (authError) {
        if (authError.message.toLowerCase().includes("email not confirmed")) {
          setError(
            "Your email address has not been verified yet. Please check your inbox for the confirmation email."
          );
        } else if (authError.message.toLowerCase().includes("invalid login credentials")) {
          setError("Invalid academic email or password. Please verify your credentials and try again.");
        } else {
          setError(authError.message);
        }
        setIsLoading(false);
        return;
      }

      if (data.session) {
        if (!rememberMe && typeof window !== "undefined") {
          // If remember me is unchecked, record session-only preference
          sessionStorage.setItem("citeverify_session_scope", "session_only");
        }
        router.push("/dashboard");
      }
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while contacting the authentication service."
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
          Sign in to CiteVerify AI
        </h2>
        <p className="mt-2 text-xs text-[#7A685D] dark:text-[#B8A898]">
          Scientific Claim Verification & Evidence Traceability Workspace
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white dark:bg-[#2A221C] py-8 px-6 shadow-brand rounded-[16px] border border-[#F0E4D2] dark:border-[#3D322A] sm:px-10">
          <form onSubmit={handleSubmit} className="space-y-5">
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
              placeholder="researcher@university.edu"
              disabled={isLoading}
            />

            <PasswordInput
              label="Password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (error) setError(null);
              }}
              placeholder="••••••••"
              disabled={isLoading}
            />

            <div className="flex items-center justify-between text-xs">
              <Checkbox
                label="Remember me on this workstation"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={isLoading}
              />
              <Link
                href="/forgot-password"
                className="text-xs font-semibold text-[#8D6E63] hover:text-[#3E2F27] dark:text-[#D7B8A8] dark:hover:text-[#F3E9DD] underline"
              >
                Forgot password?
              </Link>
            </div>

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
                Sign In to Workspace
              </Button>

              {!isConfigured && (
                <p className="text-center text-[11px] text-[#A08B78] dark:text-[#8C7A6A] pt-2">
                  Supabase authentication pending configuration in <code className="font-mono text-[10px]">.env.local</code> (submission disabled)
                </p>
              )}
            </div>
          </form>

          <div className="mt-6 text-center text-xs text-[#7A685D] dark:text-[#B8A898] border-t border-[#F0E4D2] dark:border-[#3D322A] pt-4">
            Don&apos;t have an account?{" "}
            <Link
              href="/signup"
              className="font-bold text-[#8D6E63] dark:text-[#D7B8A8] hover:underline"
            >
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
