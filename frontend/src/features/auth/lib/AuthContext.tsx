import {
  createContext,
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type { User } from "../types/auth";
import * as authApi from "../api/authApi";
import { getToken, setToken, clearToken } from "./session";
import { setAuthToken, http } from "@/shared/api/http";

const TOKEN_REFRESH_INTERVAL = 14 * 60 * 1000; // 14 minutes (before 15min expiry)

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, companyName: string) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const startRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
    }
    refreshTimerRef.current = setInterval(async () => {
      try {
        await http.post<{ access_token: string }>("/auth/refresh");
      } catch {
        // Refresh failed - token will be cleared on next API call
      }
    }, TOKEN_REFRESH_INTERVAL);
  }, []);

  const stopRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearInterval(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
  }, []);

  useEffect(() => {
    const token = getToken();
    if (token) {
      setAuthToken(token);
      authApi
        .getMe()
        .then(setUser)
        .catch(() => {
          clearToken();
          setAuthToken(null);
        })
        .finally(() => {
          setIsLoading(false);
          startRefreshTimer();
        });
    } else {
      setIsLoading(false);
    }
    return () => stopRefreshTimer();
  }, [startRefreshTimer, stopRefreshTimer]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    setToken(response.access_token);
    setUser(response.user);
    startRefreshTimer();
  }, [startRefreshTimer]);

  const register = useCallback(
    async (email: string, password: string, companyName: string) => {
      const response = await authApi.register({
        email,
        password,
        company_name: companyName,
      });
      setToken(response.access_token);
      setUser(response.user);
      startRefreshTimer();
    },
    [startRefreshTimer]
  );

  const logout = useCallback(async () => {
    stopRefreshTimer();
    await authApi.logout();
    clearToken();
    setUser(null);
  }, [stopRefreshTimer]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}