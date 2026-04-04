import { type ReactNode } from "react";
import { AuthProvider } from "@/features/auth/lib/AuthContext";

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return <AuthProvider>{children}</AuthProvider>;
}