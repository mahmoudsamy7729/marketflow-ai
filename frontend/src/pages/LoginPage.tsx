import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { AuthForm } from "@/features/auth/components/AuthForm";
import { useAuth } from "@/features/auth/hooks/useAuth";
import type { LoginInput } from "@/features/auth/types/auth";
import { ApiError } from "@/shared/api/http";

interface RedirectState {
  from?: {
    pathname?: string;
  };
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();

  async function handleSubmit(values: LoginInput) {
    try {
      setIsSubmitting(true);
      setErrorMessage(undefined);
      await login(values);
      const state = location.state as RedirectState | null;
      const redirectTo = state?.from?.pathname ?? "/dashboard";
      await navigate(redirectTo, { replace: true });
    } catch (error) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Unable to sign in right now.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthForm
      errorMessage={errorMessage}
      isSubmitting={isSubmitting}
      mode="login"
      onSubmit={handleSubmit}
    />
  );
}

