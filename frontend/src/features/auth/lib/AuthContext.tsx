import {
  createContext,
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import type { User } from "../types/auth";
import * as authApi from "../api/authApi";
import { getToken, setToken, clearToken } from "./session";
import { setAuthToken } from "@/shared/api/http";

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
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    setToken(response.access_token);
    setUser(response.user);
  }, []);

  const register = useCallback(
    async (email: string, password: string, companyName: string) => {
      const response = await authApi.register({
        email,
        password,
        company_name: companyName,
      });
      setToken(response.access_token);
      setUser(response.user);
    },
    []
  );

  const logout = useCallback(async () => {
    await authApi.logout();
    clearToken();
    setUser(null);
  }, []);

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