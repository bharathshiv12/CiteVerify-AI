"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "./sidebar";
import { TopNav } from "./top-nav";
import { SampleDataBanner } from "../ui/sample-data-banner";
import { useAuth } from "../../lib/supabase/auth-context";
import { Spinner } from "../ui/spinner";

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Fail closed: If auth check is complete and no valid user session exists,
    // redirect to /login immediately.
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [isLoading, user, router]);

  // Loading state while verifying credentials or resolving session
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#FFF8E8] dark:bg-[#1E1814] text-[#3E2F27] dark:text-[#F3E9DD]">
        <Spinner size="lg" />
        <p className="mt-4 text-xs font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">
          Verifying secure session credentials...
        </p>
      </div>
    );
  }

  // If unauthenticated, do not render protected children (fail closed)
  if (!user) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#FFF8E8] dark:bg-[#1E1814] text-[#3E2F27] dark:text-[#F3E9DD]">
        <Spinner size="lg" />
        <p className="mt-4 text-xs font-semibold text-[#8D6E63] dark:text-[#D7B8A8]">
          Redirecting to authentication...
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#FFF8E8] dark:bg-[#1E1814] text-[#3E2F27] dark:text-[#F3E9DD]">
      <SampleDataBanner />
      <div className="flex-1 flex flex-row w-full">
        {/* Responsive Sidebar */}
        <Sidebar
          isMobileOpen={isMobileMenuOpen}
          onCloseMobile={() => setIsMobileMenuOpen(false)}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <TopNav onOpenMobileMenu={() => setIsMobileMenuOpen(true)} />
          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
