"use client";

import React, { useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Menu,
  Bell,
  Sun,
  Moon,
  Laptop,
  Search,
  CheckCircle2,
  ChevronRight,
  User,
} from "lucide-react";
import { useTheme } from "next-themes";
import { useAuth } from "../../lib/supabase/auth-context";
import { SearchInput } from "../ui/search-input";
import { getRegisteredDocuments } from "../../lib/document-registry";

interface TopNavProps {
  onOpenMobileMenu: () => void;
}

export function TopNav({ onOpenMobileMenu }: TopNavProps) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const { user, fullName, isConfigured } = useAuth();

  const [searchQuery, setSearchQuery] = useState("");
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  // Derive title from pathname
  const getPageTitle = () => {
    if (pathname === "/dashboard") return "Dashboard";
    if (pathname.startsWith("/verify")) return "Document Verification";
    if (pathname.startsWith("/reports")) return "Verification Reports";
    if (pathname === "/history") return "Verification History";
    if (pathname === "/settings") return "Workspace Settings";
    if (pathname === "/design-system") return "Design System Reference";
    return "CiteVerify AI";
  };

  // Local device search results
  const docs = typeof window !== "undefined" ? getRegisteredDocuments(user?.id) : [];
  const searchResults = searchQuery.trim()
    ? docs.filter((d) => d.filename.toLowerCase().includes(searchQuery.toLowerCase()))
    : [];

  return (
    <header className="sticky top-0 z-20 w-full h-16 bg-white/80 dark:bg-[#2A221C]/80 backdrop-blur-md border-b border-[#F0E4D2] dark:border-[#3D322A] px-4 sm:px-6 flex items-center justify-between gap-4">
      {/* Left side: Mobile menu toggle + Page title & breadcrumbs */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileMenu}
          className="lg:hidden p-2 rounded-lg text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD] hover:bg-[#FFF0D6] dark:hover:bg-[#33291F]"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex flex-col">
          {/* Breadcrumbs for nested routes */}
          {pathname !== "/dashboard" && (
            <div className="flex items-center gap-1 text-[11px] text-[#7A685D] dark:text-[#B8A898]">
              <Link href="/dashboard" className="hover:underline">
                Home
              </Link>
              <ChevronRight className="w-3 h-3 text-[#A08B78]" />
              <span className="truncate max-w-[150px] sm:max-w-xs">{getPageTitle()}</span>
            </div>
          )}
          <h1 className="text-base sm:text-lg font-bold font-heading text-[#3E2F27] dark:text-[#F3E9DD] leading-tight">
            {getPageTitle()}
          </h1>
        </div>
      </div>

      {/* Right side: Search, Theme Toggle, Notifications, User Profile */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Global device search */}
        <div className="relative hidden md:block w-56 lg:w-72">
          <SearchInput
            value={searchQuery}
            onChange={(val) => {
              setSearchQuery(val);
              setShowSearchResults(Boolean(val.trim()));
            }}
            placeholder="Search local documents..."
          />
          {showSearchResults && (
            <div className="absolute top-full left-0 right-0 mt-1 p-2 rounded-[10px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-xl z-50 text-xs">
              <p className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-[#7A685D] dark:text-[#B8A898]">
                Registered Local Documents
              </p>
              {searchResults.length > 0 ? (
                searchResults.map((d) => (
                  <Link
                    key={d.document_id}
                    href={`/reports/${d.document_id}`}
                    onClick={() => setShowSearchResults(false)}
                    className="block px-2.5 py-1.5 rounded-md hover:bg-[#FFF0D6] dark:hover:bg-[#33291F] text-[#3E2F27] dark:text-[#F3E9DD] truncate"
                  >
                    📄 {d.filename}
                  </Link>
                ))
              ) : (
                <p className="px-2 py-1.5 text-stone-500 italic">No matching local documents.</p>
              )}
            </div>
          )}
        </div>

        {/* Theme Mode Toggle */}
        <div className="flex items-center p-1 rounded-lg bg-[#FFF0D6]/60 dark:bg-[#33291F]/60 border border-[#F0E4D2] dark:border-[#3D322A]">
          <button
            onClick={() => setTheme("light")}
            className={`p-1.5 rounded-md transition-colors ${
              theme === "light"
                ? "bg-white text-[#3E2F27] shadow-sm"
                : "text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD]"
            }`}
            title="Light theme"
            aria-label="Light theme"
          >
            <Sun className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setTheme("dark")}
            className={`p-1.5 rounded-md transition-colors ${
              theme === "dark"
                ? "bg-[#2A221C] text-[#F4B860] shadow-sm"
                : "text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD]"
            }`}
            title="Dark theme"
            aria-label="Dark theme"
          >
            <Moon className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setTheme("system")}
            className={`p-1.5 rounded-md transition-colors ${
              theme === "system"
                ? "bg-white dark:bg-[#2A221C] text-[#3E2F27] dark:text-[#F3E9DD] shadow-sm"
                : "text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD]"
            }`}
            title="System theme"
            aria-label="System theme"
          >
            <Laptop className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Notifications Popover */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-lg text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD] hover:bg-[#FFF0D6] dark:hover:bg-[#33291F] transition-colors relative"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-full mt-2 w-72 rounded-[14px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-xl p-3 z-50 animate-in fade-in duration-150">
              <div className="flex items-center justify-between pb-2 border-b border-[#F0E4D2] dark:border-[#3D322A] text-xs font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                <span>Document Status Notifications</span>
                <span className="text-[10px] text-[#7A685D] dark:text-[#B8A898] font-normal">
                  Local device
                </span>
              </div>
              <div className="py-3 text-center text-xs text-[#7A685D] dark:text-[#B8A898]">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 mx-auto mb-1" />
                <p>No unread verification alerts.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
