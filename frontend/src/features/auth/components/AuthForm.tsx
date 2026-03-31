import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { z } from "zod";

import type { LoginInput, RegisterInput } from "@/features/auth/types/auth";
import { Button } from "@/shared/ui/Button";
import { FieldError } from "@/shared/ui/FieldError";
import { Input } from "@/shared/ui/Input";

export type AuthMode = "login" | "register";

type AuthFormValues = {
  email: string;
  password: string;
  companyName: string;
};

interface AuthFormProps {
  errorMessage?: string;
  isSubmitting: boolean;
  mode: AuthMode;
  onSubmit: (values: LoginInput | RegisterInput) => Promise<void>;
}

function createSchema(mode: AuthMode) {
  return z
    .object({
      email: z.string().trim().email("Enter a valid email address."),
      password: z
        .string()
        .min(8, "Password must be at least 8 characters."),
      companyName: z.string().trim().optional(),
    })
    .superRefine((value, context) => {
      if (mode === "register" && !value.companyName) {
        context.addIssue({
          code: z.ZodIssueCode.custom,
          message: "Company name is required.",
          path: ["companyName"],
        });
      }
    });
}

const content = {
  login: {
    title: "Welcome back",
    description: "Sign in to manage campaigns, content plans, and publishing workflows.",
    submitLabel: "Sign in",
    switchLabel: "Need an account? Create one",
    switchTo: "/register",
  },
  register: {
    title: "Create your workspace",
    description: "Start with a clean account setup and connect the channels you want to automate.",
    submitLabel: "Create account",
    switchLabel: "Already have an account? Sign in",
    switchTo: "/login",
  },
} as const;

export function AuthForm({
  errorMessage,
  isSubmitting,
  mode,
  onSubmit,
}: AuthFormProps) {
  const schema = createSchema(mode);
  const formContent = content[mode];
  const {
    formState: { errors },
    handleSubmit,
    register,
  } = useForm<AuthFormValues>({
    defaultValues: {
      email: "",
      password: "",
      companyName: "",
    },
    resolver: zodResolver(schema),
  });

  function handleFormSubmit(values: AuthFormValues) {
    const payload =
      mode === "register"
        ? {
            email: values.email.trim(),
            password: values.password,
            companyName: values.companyName.trim(),
          }
        : {
            email: values.email.trim(),
            password: values.password,
          };

    return onSubmit(payload);
  }

  return (
    <form
      className="space-y-5"
      onSubmit={(event) => {
        void handleSubmit(handleFormSubmit)(event);
      }}
    >
      <div>
        <h1 className="text-3xl font-semibold text-white">{formContent.title}</h1>
        <p className="mt-2 text-sm text-slate-400">{formContent.description}</p>
      </div>

      {mode === "register" ? (
        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-200" htmlFor="companyName">
            Company name
          </label>
          <Input
            autoComplete="organization"
            id="companyName"
            placeholder="Acme Studio"
            {...register("companyName")}
          />
          <FieldError message={errors.companyName?.message} />
        </div>
      ) : null}

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-200" htmlFor="email">
          Email
        </label>
        <Input
          autoComplete="email"
          id="email"
          placeholder="you@company.com"
          type="email"
          {...register("email")}
        />
        <FieldError message={errors.email?.message} />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-slate-200" htmlFor="password">
          Password
        </label>
        <Input
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          id="password"
          placeholder="Minimum 8 characters"
          type="password"
          {...register("password")}
        />
        <FieldError message={errors.password?.message} />
      </div>

      {errorMessage ? <FieldError message={errorMessage} /> : null}

      <div className="space-y-3">
        <Button className="w-full" isLoading={isSubmitting} type="submit">
          {formContent.submitLabel}
        </Button>
        <Link className="block text-center text-sm text-cyan-200 hover:text-cyan-100" to={formContent.switchTo}>
          {formContent.switchLabel}
        </Link>
      </div>
    </form>
  );
}
