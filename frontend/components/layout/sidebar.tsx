"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileCheck,
  FileText,
  History,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  User,
} from "lucide-react";
import { Logo } from "../brand/logo";
import { useAuth } from "../../lib/supabase/auth-context";

interface SidebarProps {
  isMobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export function Sidebar({ isMobileOpen = false, onCloseMobile }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { user, fullName, institution, signOut, isConfigured } = useAuth();

  // Exactly five navigation items, in strict order:
  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Verify Document", href: "/verify", icon: FileCheck },
    { label: "Reports", href: "/reports", icon: FileText },
    { label: "History", href: "/history", icon: History },
    { label: "Settings", href: "/settings", icon: Settings },
  ];

  const getInitials = (name?: string, email?: string) => {
    if (name?.trim()) {
      const parts = name.trim().split(" ");
      return parts.length >= 2 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : parts[0].slice(0, 2).toUpperCase();
    }
    if (email) return email.slice(0, 2).toUpperCase();
    return "CV";
  };

  const navContent = (
    <div className="flex flex-col h-full bg-[#FFF0D6] dark:bg-[#33291F] border-r border-[#F0E4D2] dark:border-[#3D322A] select-none">
      {/* Brand Header */}
      <div className="p-5 flex items-center justify-between border-b border-[#F0E4D2] dark:border-[#3D322A]">
        <Logo iconOnly={isCollapsed} size="md" />
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="hidden xl:flex p-1.5 rounded-lg text-[#7A685D] hover:text-[#3E2F27] dark:hover:text-[#F3E9DD] hover:bg-[#FFDCA8]/50 dark:hover:bg-[#4A3A28]/50 transition-colors"
          title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Main Navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => onCloseMobile?.()}
              aria-current={isActive ? "page" : undefined}
              className={`group flex items-center gap-3 px-3 py-2.5 rounded-[10px] text-sm font-medium transition-colors relative ${
                isActive
                  ? "bg-[#FFDCA8] dark:bg-[#4A3A28] text-[#3E2F27] dark:text-[#F3E9DD] font-semibold"
                  : "text-[#7A685D] dark:text-[#B8A898] hover:bg-[#FFDCA8]/40 dark:hover:bg-[#4A3A28]/40 hover:text-[#3E2F27] dark:hover:text-[#F3E9DD]"
              }`}
              title={isCollapsed ? item.label : undefined}
            >
              {/* 3px primary left indicator */}
              {isActive && (
                <span
                  className="absolute left-0 top-1.5 bottom-1.5 w-[3px] bg-[#F4B860] rounded-r"
                  aria-hidden="true"
                />
              )}
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User profile footer */}
      <div className="p-3 border-t border-[#F0E4D2] dark:border-[#3D322A]">
        <div className="flex items-center justify-between p-2 rounded-[10px] bg-white/60 dark:bg-[#2A221C]/60 border border-[#F0E4D2] dark:border-[#3D322A]">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-[#F4B860] text-[#3E2F27] font-bold text-xs flex items-center justify-center flex-shrink-0 font-mono">
              {getInitials(fullName, user?.email)}
            </div>
            {!isCollapsed && (
              <div className="min-w-0">
                <p className="text-xs font-bold text-[#3E2F27] dark:text-[#F3E9DD] truncate">
                  {fullName || user?.email || "Academic Guest"}
                </p>
                <p className="text-[10px] text-[#7A685D] dark:text-[#B8A898] truncate">
                  {institution || (isConfigured ? "Researcher" : "Guest Mode")}
                </p>
              </div>
            )}
          </div>

          {!isCollapsed && (
            <button
              onClick={() => signOut()}
              className="p-1.5 text-[#7A685D] hover:text-[#8F2E2E] dark:hover:text-[#fca5a5] rounded-lg transition-colors"
              title="Log out"
              aria-label="Log out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop / Tablet Sidebar */}
      <aside
        className={`hidden lg:flex flex-col h-screen sticky top-0 transition-all duration-200 z-30 ${
          isCollapsed ? "w-[72px]" : "w-[250px]"
        }`}
      >
        {navContent}
      </aside>

      {/* Mobile Slide-out Drawer with Backdrop */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
            onClick={onCloseMobile}
            aria-hidden="true"
          />
          <div className="fixed inset-y-0 left-0 w-[270px] bg-[#FFF0D6] dark:bg-[#33291F] shadow-2xl z-50 animate-in slide-in-from-left duration-200">
            {navContent}
          </div>
        </div>
      )}
    </>
  );
}
