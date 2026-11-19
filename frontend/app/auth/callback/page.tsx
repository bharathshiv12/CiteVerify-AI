"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getSupabaseClient } from "../../../lib/supabase/client";
import { Spinner } from "../../../components/ui/spinner";

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) {
      router.push("/dashboard");
      return;
    }

    supabase.auth.getSession().then(() => {
      router.push("/dashboard");
    });
  }, [router]);

  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] flex flex-col items-center justify-center p-4 text-center">
      <Spinner size="lg" />
      <p className="mt-4 text-sm font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">
        Completing academic authentication...
      </p>
    </div>
  );
}
