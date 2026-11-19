import React from "react";
import Link from "next/link";
import { Logo } from "../components/brand/logo";
import { Button } from "../components/ui/button";
import { FileQuestion, ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-[#FFF8E8] dark:bg-[#1E1814] flex flex-col items-center justify-center p-6 text-center text-[#3E2F27] dark:text-[#F3E9DD]">
      <Logo size="lg" withLink={false} />
      <div className="mt-8 w-16 h-16 rounded-full bg-[#FFF0D6] dark:bg-[#33291F] text-[#8D6E63] dark:text-[#D7B8A8] flex items-center justify-center mx-auto">
        <FileQuestion className="w-8 h-8" />
      </div>
      <h1 className="mt-4 text-3xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
        404 — Research Page Not Found
      </h1>
      <p className="mt-2 text-xs sm:text-sm text-[#7A685D] dark:text-[#B8A898] max-w-md leading-relaxed">
        The requested verification route, document ID, or report could not be found in the system registry.
      </p>
      <div className="mt-6">
        <Link href="/dashboard">
          <Button variant="primary" size="standard" leftIcon={<ArrowLeft className="w-4 h-4" />}>
            Return to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
}
