"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User, Session } from "@supabase/supabase-js";
import { getSupabaseClient } from "./client";

export interface AuthContextType {
  user: User | null;
  session: Session | null;
  fullName: string;
  institution: string;
  isConfigured: boolean;
  isLoading: boolean;
  signOut: () => Promise<void>;
}

const defaultContext: AuthContextType = {
  user: null,
  session: null,
  fullName: "",
  institution: "",
  isConfigured: false,
  isLoading: true,
  signOut: async () => {},
};

const AuthContext = createContext<AuthContextType>(defaultContext);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [fullName, setFullName] = useState<string>("");
  const [institution, setInstitution] = useState<string>("");
  const [isConfigured, setIsConfigured] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) {
      setIsConfigured(false);
      setUser(null);
      setSession(null);
      setIsLoading(false);
      return;
    }

    setIsConfigured(true);

    supabase.auth
      .getSession()
      .then(({ data: { session: initialSession } }) => {
        setSession(initialSession);
        setUser(initialSession?.user ?? null);
        if (initialSession?.user) {
          const meta = initialSession.user.user_metadata || {};
          setFullName(meta.full_name || meta.name || "");
          setInstitution(meta.institution || "");
        }
      })
      .catch((err) => {
        console.error("Failed to retrieve Supabase session:", err);
      })
      .finally(() => {
        setIsLoading(false);
      });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, currentSession) => {
      setSession(currentSession);
      setUser(currentSession?.user ?? null);
      if (currentSession?.user) {
        const meta = currentSession.user.user_metadata || {};
        setFullName(meta.full_name || meta.name || "");
        setInstitution(meta.institution || "");
      } else {
        setFullName("");
        setInstitution("");
      }
      setIsLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const signOut = async () => {
    const supabase = getSupabaseClient();
    if (supabase) {
      await supabase.auth.signOut();
    }
    setUser(null);
    setSession(null);
    setFullName("");
    setInstitution("");
    if (typeof window !== "undefined") {
      sessionStorage.removeItem("citeverify_session_scope");
      window.location.href = "/login";
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        fullName,
        institution,
        isConfigured,
        isLoading,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  return useContext(AuthContext);
}
