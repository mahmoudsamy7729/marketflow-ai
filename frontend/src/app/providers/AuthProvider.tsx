import { useEffect, useState } from "react";
import type { PropsWithChildren } from "react";

import {
  loginUser,
  logoutUser,
  refreshSession,
  registerUser,
} from "@/features/auth/api/authApi";
import { AuthContext } from "@/features/auth/lib/authContext";
import {
  clearAccessToken,
  setAccessToken,
} from "@/features/auth/lib/session";
import type { AuthStatus } from "@/features/auth/lib/authContext";
import type { User } from "@/features/auth/types/auth";

export function AuthProvider({ children }: PropsWithChildren) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let isActive = true;

    async function bootstrapSession() {
      try {
        const session = await refreshSession();
        if (!isActive) {
          return;
        }

        setAccessToken(session.accessToken);
        setUser(session.user);
        setStatus("authenticated");
      } catch {
        if (!isActive) {
          return;
        }

        clearAccessToken();
        setUser(null);
        setStatus("unauthenticated");
      }
    }

    void bootstrapSession();

    return () => {
      isActive = false;
    };
  }, []);

  async function login(payload: Parameters<typeof loginUser>[0]) {
    const session = await loginUser(payload);
    setAccessToken(session.accessToken);
    setUser(session.user);
    setStatus("authenticated");
  }

  async function register(payload: Parameters<typeof registerUser>[0]) {
    const session = await registerUser(payload);
    setAccessToken(session.accessToken);
    setUser(session.user);
    setStatus("authenticated");
  }

  async function logout() {
    try {
      await logoutUser();
    } finally {
      clearAccessToken();
      setUser(null);
      setStatus("unauthenticated");
    }
  }

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: status === "authenticated",
        login,
        logout,
        register,
        status,
        user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
