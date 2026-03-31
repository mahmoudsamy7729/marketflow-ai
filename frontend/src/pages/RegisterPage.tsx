import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { AuthForm } from "@/features/auth/components/AuthForm";
import { useAuth } from "@/features/auth/hooks/useAuth";
import type { LoginInput, RegisterInput } from "@/features/auth/types/auth";
import { ApiError } from "@/shared/api/http";

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>();

  async function handleSubmit(values: LoginInput | RegisterInput) {
    try {
      setIsSubmitting(true);
      setErrorMessage(undefined);
      await register(values as RegisterInput);
      void navigate("/dashboard", { replace: true });
    } catch (error) {
      setErrorMessage(
        error instanceof ApiError ? error.message : "Unable to create the account right now.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthForm
      errorMessage={errorMessage}
      isSubmitting={isSubmitting}
      mode="register"
      onSubmit={handleSubmit}
    />
  );
}

