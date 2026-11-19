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

function GoogleIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
      />
    </svg>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const { user, isConfigured, isLoading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // Field validation checks for button enabling
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isEmailValid = emailRegex.test(email.trim());
  const isPasswordPresent = password.length > 0;
  const isFormValid = isEmailValid && isPasswordPresent;
  const isSubmitDisabled = !isConfigured || isLoading || isGoogleLoading || !isFormValid;

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

  const handleGoogleSignIn = async () => {
    setError(null);

    if (!isConfigured) {
      setError(
        "Authentication service is currently unavailable. Supabase environment credentials are not configured on this deployment."
      );
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) {
      setError("Failed to initialize authentication client.");
      return;
    }

    setIsGoogleLoading(true);

    try {
      const redirectTo =
        typeof window !== "undefined"
          ? `${window.location.origin}/auth/callback`
          : undefined;

      const { error: oauthError } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo,
        },
      });

      if (oauthError) {
        setError(oauthError.message);
        setIsGoogleLoading(false);
      }
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while initiating Google Sign-In."
      );
      setIsGoogleLoading(false);
    }
  };

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
          {/* Continue with Google */}
          <div>
            <Button
              type="button"
              variant="outline"
              size="standard"
              className="w-full bg-white dark:bg-[#2A221C] border-[#D4C3B3] dark:border-[#524338] text-[#3E2F27] dark:text-[#F3E9DD] hover:bg-[#FFF8E8] dark:hover:bg-[#352B24] font-medium shadow-sm transition-all text-xs sm:text-sm"
              onClick={handleGoogleSignIn}
              isLoading={isGoogleLoading}
              disabled={!isConfigured || isLoading || isGoogleLoading}
              leftIcon={<GoogleIcon className="w-4 h-4 flex-shrink-0" />}
            >
              Continue with Google
            </Button>

            <div className="relative my-5">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[#F0E4D2] dark:border-[#3D322A]" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white dark:bg-[#2A221C] px-3 text-[#A08B78] dark:text-[#8C7A6A] font-semibold tracking-wider text-[11px]">
                  Or continue with academic email
                </span>
              </div>
            </div>
          </div>

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
