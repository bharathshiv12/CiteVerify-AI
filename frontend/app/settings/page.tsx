"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/layout/app-shell";
import { Input } from "../../components/ui/input";
import { PasswordInput } from "../../components/ui/password-input";
import { Button } from "../../components/ui/button";
import { Checkbox } from "../../components/ui/checkbox";
import { useAuth } from "../../lib/supabase/auth-context";
import { getSupabaseClient } from "../../lib/supabase/client";
import { useTheme } from "next-themes";
import {
  User,
  Shield,
  Bell,
  Sun,
  Moon,
  Laptop,
  CheckCircle2,
  AlertCircle,
  KeyRound,
  LogOut,
} from "lucide-react";

export default function SettingsPage() {
  const { user, fullName: contextFullName, institution: contextInstitution, isConfigured, signOut } = useAuth();
  const { theme, setTheme } = useTheme();

  const [fullName, setFullName] = useState(contextFullName || "");
  const [institution, setInstitution] = useState(contextInstitution || "");
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [profileMessage, setProfileMessage] = useState<string | null>(null);

  // Security password state
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isUpdatingPassword, setIsUpdatingPassword] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  // Notification preferences stored locally
  const [notifyAnalysisDone, setNotifyAnalysisDone] = useState(true);
  const [notifyHumanReviewNeeded, setNotifyHumanReviewNeeded] = useState(true);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isConfigured) {
      setProfileMessage("Profile saved to local guest session.");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) return;

    setIsSavingProfile(true);
    setProfileMessage(null);

    const { error } = await supabase.auth.updateUser({
      data: {
        full_name: fullName.trim(),
        institution: institution.trim(),
      },
    });

    setIsSavingProfile(false);
    if (error) {
      setProfileMessage(`Error: ${error.message}`);
    } else {
      setProfileMessage("Profile updated successfully!");
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setPasswordError("Passwords do not match.");
      return;
    }

    if (!isConfigured) {
      setPasswordMessage("Password simulated update for local session.");
      return;
    }

    const supabase = getSupabaseClient();
    if (!supabase) return;

    setIsUpdatingPassword(true);
    setPasswordError(null);
    setPasswordMessage(null);

    const { error } = await supabase.auth.updateUser({
      password: newPassword,
    });

    setIsUpdatingPassword(false);
    if (error) {
      setPasswordError(error.message);
    } else {
      setPasswordMessage("Password changed successfully!");
      setNewPassword("");
      setConfirmPassword("");
    }
  };

  return (
    <AppShell>
      <div className="max-w-5xl mx-auto space-y-8 pb-16">
        {/* Header */}
        <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand">
          <h2 className="text-2xl font-extrabold font-heading text-[#8D6E63] dark:text-[#D7B8A8]">
            Workspace Settings
          </h2>
          <p className="mt-1 text-xs text-[#7A685D] dark:text-[#B8A898]">
            Manage academic profile, display preferences, and security credentials
          </p>
        </div>

        {/* Two-column layout on desktop */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Section 1: Academic Profile */}
          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-5">
            <div className="flex items-center gap-2 pb-3 border-b border-[#F0E4D2] dark:border-[#3D322A]">
              <User className="w-4 h-4 text-[#8D6E63] dark:text-[#D7B8A8]" />
              <h3 className="text-sm font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                Academic Profile
              </h3>
            </div>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <Input
                label="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Dr. Alan Grant"
              />

              <Input
                label="Academic Email"
                value={user?.email || "guest.researcher@citeverify.local"}
                disabled
                hint="Managed via authentication provider"
              />

              <Input
                label="Institution or University"
                value={institution}
                onChange={(e) => setInstitution(e.target.value)}
                placeholder="MIT / Max Planck Institute"
              />

              {profileMessage && (
                <p className="text-xs text-emerald-700 dark:text-emerald-400 font-medium">
                  {profileMessage}
                </p>
              )}

              <Button
                type="submit"
                variant="primary"
                size="compact"
                isLoading={isSavingProfile}
              >
                Save Profile Changes
              </Button>
            </form>
          </div>

          {/* Section 2: Display & Notifications */}
          <div className="p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-5">
            <div className="flex items-center gap-2 pb-3 border-b border-[#F0E4D2] dark:border-[#3D322A]">
              <Sun className="w-4 h-4 text-[#8D6E63] dark:text-[#D7B8A8]" />
              <h3 className="text-sm font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                Theme & Interface Preferences
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#3E2F27] dark:text-[#F3E9DD] mb-2">
                  Interface Color Theme
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setTheme("light")}
                    className={`p-3 rounded-[10px] text-xs font-semibold flex items-center justify-center gap-2 border transition-all ${
                      theme === "light"
                        ? "bg-[#FFF0D6] border-[#F4B860] text-[#3E2F27] shadow-sm"
                        : "bg-white dark:bg-[#2A221C] border-[#F0E4D2] dark:border-[#3D322A] text-[#7A685D]"
                    }`}
                  >
                    <Sun className="w-4 h-4" /> Light
                  </button>
                  <button
                    type="button"
                    onClick={() => setTheme("dark")}
                    className={`p-3 rounded-[10px] text-xs font-semibold flex items-center justify-center gap-2 border transition-all ${
                      theme === "dark"
                        ? "bg-[#33291F] border-[#F4B860] text-[#F4B860] shadow-sm"
                        : "bg-white dark:bg-[#2A221C] border-[#F0E4D2] dark:border-[#3D322A] text-[#7A685D]"
                    }`}
                  >
                    <Moon className="w-4 h-4" /> Dark
                  </button>
                  <button
                    type="button"
                    onClick={() => setTheme("system")}
                    className={`p-3 rounded-[10px] text-xs font-semibold flex items-center justify-center gap-2 border transition-all ${
                      theme === "system"
                        ? "bg-[#FFF0D6] dark:bg-[#33291F] border-[#F4B860] text-[#3E2F27] dark:text-[#F3E9DD]"
                        : "bg-white dark:bg-[#2A221C] border-[#F0E4D2] dark:border-[#3D322A] text-[#7A685D]"
                    }`}
                  >
                    <Laptop className="w-4 h-4" /> System
                  </button>
                </div>
              </div>

              <div className="pt-3 border-t border-[#F0E4D2] dark:border-[#3D322A] space-y-3">
                <span className="block text-xs font-semibold text-[#3E2F27] dark:text-[#F3E9DD]">
                  In-App Notification Preferences
                </span>
                <Checkbox
                  label="Notify when document analysis finishes"
                  checked={notifyAnalysisDone}
                  onChange={(e) => setNotifyAnalysisDone(e.target.checked)}
                />
                <Checkbox
                  label="Notify when claims require human audit"
                  checked={notifyHumanReviewNeeded}
                  onChange={(e) => setNotifyHumanReviewNeeded(e.target.checked)}
                />
                <p className="text-[11px] text-[#A08B78] dark:text-[#8C7A6A] italic">
                  Note: Notifications are in-app local alerts only. Email alerts are not dispatched.
                </p>
              </div>
            </div>
          </div>

          {/* Section 3: Password & Security */}
          <div className="lg:col-span-2 p-6 rounded-[16px] bg-white dark:bg-[#2A221C] border border-[#F0E4D2] dark:border-[#3D322A] shadow-brand space-y-5">
            <div className="flex items-center gap-2 pb-3 border-b border-[#F0E4D2] dark:border-[#3D322A]">
              <KeyRound className="w-4 h-4 text-[#8D6E63] dark:text-[#D7B8A8]" />
              <h3 className="text-sm font-bold text-[#3E2F27] dark:text-[#F3E9DD]">
                Security Credentials
              </h3>
            </div>

            <form onSubmit={handleUpdatePassword} className="max-w-xl space-y-4">
              <PasswordInput
                label="New Password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                showStrengthChecklist
                placeholder="••••••••"
              />

              <PasswordInput
                label="Confirm New Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
              />

              {passwordError && (
                <p className="text-xs text-red-600 dark:text-red-400 font-medium">
                  {passwordError}
                </p>
              )}

              {passwordMessage && (
                <p className="text-xs text-emerald-700 dark:text-emerald-400 font-medium">
                  {passwordMessage}
                </p>
              )}

              <Button
                type="submit"
                variant="secondary"
                size="compact"
                isLoading={isUpdatingPassword}
              >
                Change Password
              </Button>
            </form>

            <div className="pt-4 border-t border-[#F0E4D2] dark:border-[#3D322A] flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-[#3E2F27] dark:text-[#F3E9DD]">
                  Account Session
                </p>
                <p className="text-[11px] text-[#7A685D] dark:text-[#B8A898]">
                  Sign out of your active browser session on this device
                </p>
              </div>
              <Button
                variant="danger"
                size="compact"
                onClick={() => signOut()}
                leftIcon={<LogOut className="w-3.5 h-3.5" />}
              >
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
