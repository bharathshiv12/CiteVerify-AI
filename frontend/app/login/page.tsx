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
import { AlertCircle, ArrowRight, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { isConfigured } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isConfigured) {
      // If auth is not configured, redirect to dashboard in guest mode
      router.push("/dashboard");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) return;

    setIsLoading(true);
    setError(null);

    const { error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    setIsLoading(false);
    if (authError) {
      setError("Invalid login credentials. Please check your email and password.");
    } else {
      router.push("/dashboard");
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
          {!isConfigured && (
            <div className="mb-6 p-3.5 rounded-[10px] bg-[#FFF0D6] dark:bg-[#33291F] border border-[#F4B860]/40 text-xs space-y-1 text-[#3E2F27] dark:text-[#F3E9DD]">
              <div className="flex items-center gap-1.5 font-bold text-[#8D6E63] dark:text-[#D7B8A8]">
                <AlertCircle className="w-4 h-4 text-[#B77B35]" />
                Authentication is not configured.
              </div>
              <p className="text-[11px] text-[#7A685D] dark:text-[#B8A898] leading-relaxed">
                Supabase environment keys (<code className="font-mono text-[10px]">NEXT_PUBLIC_SUPABASE_URL</code>) are not configured. You can continue directly to the research workspace in local guest mode.
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

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Academic Email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="researcher@university.edu"
              disabled={!isConfigured}
            />

            <PasswordInput
              label="Password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={!isConfigured}
            />

            <div className="flex items-center justify-between text-xs">
              <Checkbox
                label="Remember me"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={!isConfigured}
              />
              <Link
                href="/forgot-password"
                className="text-xs font-semibold text-[#8D6E63] hover:text-[#3E2F27] dark:text-[#D7B8A8] dark:hover:text-[#F3E9DD] underline"
              >
                Forgot password?
              </Link>
            </div>

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
              Sign In
            </Button>
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
