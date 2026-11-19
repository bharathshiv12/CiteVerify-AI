"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSupabaseClient } from "../../../lib/supabase/client";
import { Spinner } from "../../../components/ui/spinner";

export default function AuthCallbackPage() {
  const router = useRouter();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) {
      router.push("/login");
      return;
    }

    const processAuth = async () => {
      try {
        if (typeof window !== "undefined") {
          const url = new URL(window.location.href);
          const code = url.searchParams.get("code");
          const next = url.searchParams.get("next");
          const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
          const type = hashParams.get("type") || url.searchParams.get("type");

          // Check if OAuth provider returned an error description
          const oauthError =
            url.searchParams.get("error_description") ||
            hashParams.get("error_description") ||
            url.searchParams.get("error") ||
            hashParams.get("error");

          if (oauthError) {
            setErrorMsg(oauthError);
            return;
          }

          if (code) {
            const { error } = await supabase.auth.exchangeCodeForSession(code);
            if (error) {
              setErrorMsg(error.message);
              return;
            }
          } else {
            const { error } = await supabase.auth.getSession();
            if (error) {
              setErrorMsg(error.message);
              return;
            }
          }

          if (type === "recovery" || next === "/reset-password") {
            router.push("/reset-password");
          } else if (next) {
            router.push(next);
          } else {
            router.push("/dashboard");
          }
        }
      } catch (err: unknown) {
        setErrorMsg(err instanceof Error ? err.message : "Authentication processing error.");
      }
    };

    processAuth();
  }, [router]);

  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] flex flex-col items-center justify-center p-4 text-center">
      {errorMsg ? (
        <div className="max-w-md p-6 bg-white dark:bg-[#2A221C] rounded-xl border border-[#B94D4D]/30 shadow-brand text-center">
          <p className="text-sm font-semibold text-[#8F2E2E] dark:text-[#fca5a5] mb-4">
            {errorMsg}
          </p>
          <button
            onClick={() => router.push("/login")}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-[#F4B860] text-[#3E2F27]"
          >
            Return to Login
          </button>
        </div>
      ) : (
        <>
          <Spinner size="lg" />
          <p className="mt-4 text-sm font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">
            Completing academic authentication...
          </p>
        </>
      )}
    </div>
  );
}
