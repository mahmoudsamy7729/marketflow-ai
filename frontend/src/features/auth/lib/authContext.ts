import { createContext } from "react";

import type {
  LoginInput,
  RegisterInput,
  User,
} from "@/features/auth/types/auth";

export type AuthStatus = "loading" | "authenticated" | "unauthenticated";

export interface AuthContextValue {
  isAuthenticated: boolean;
  login: (payload: LoginInput) => Promise<void>;
  logout: () => Promise<void>;
  register: (payload: RegisterInput) => Promise<void>;
  status: AuthStatus;
  user: User | null;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
