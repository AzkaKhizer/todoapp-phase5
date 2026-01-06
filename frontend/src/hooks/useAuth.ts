"use client";

import { useRouter } from "next/navigation";
import { useCallback } from "react";

import { useAuthContext } from "@/contexts/AuthContext";

export function useAuth() {
  const router = useRouter();
  const {
    user,
    isLoading,
    isAuthenticated,
    login: contextLogin,
    register: contextRegister,
    logout: contextLogout,
    error,
  } = useAuthContext();

  const login = useCallback(
    async (email: string, password: string) => {
      await contextLogin({ email, password });
      router.push("/dashboard");
    },
    [contextLogin, router]
  );

  const register = useCallback(
    async (email: string, password: string) => {
      await contextRegister({ email, password });
      router.push("/dashboard");
    },
    [contextRegister, router]
  );

  const logout = useCallback(() => {
    contextLogout();
    router.push("/login");
  }, [contextLogout, router]);

  return {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    error,
  };
}
