import type { FormEvent } from "react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { HttpError } from "@/shared/api/http";

type AuthMode = "login" | "register";

interface AuthPageProps {
  mode: AuthMode;
}

const authContent = {
  login: {
    eyebrow: "Auth_Sequence // 01",
    title: "Re-enter the system.",
    description:
      "Access the campaign engine, queue state, and publishing controls from one authenticated workspace.",
    submitLabel: "Sign in",
    altPrompt: "Need a workspace?",
    altLabel: "Create one",
    altTo: "/register",
    helper: "Use the credentials assigned to your company workspace.",
  },
  register: {
    eyebrow: "Auth_Sequence // 02",
    title: "Construct your workspace.",
    description:
      "Create the company account that anchors strategy, channels, content generation, and delivery operations.",
    submitLabel: "Create account",
    altPrompt: "Already have access?",
    altLabel: "Sign in",
    altTo: "/login",
    helper: "Registration UI is ready for the live auth wiring behind the backend endpoints.",
  },
} as const;

const telemetryRows = [
  "JWT-backed auth sessions",
  "Company-scoped campaign workspaces",
  "Channel connection and page selection",
  "AI plans, posts, and publishing states",
] as const;

const rightRailPoints = [
  {
    label: "Secure access",
    body: "Auth unlocks campaign control, queue state, and publishing actions.",
  },
  {
    label: "One workspace",
    body: "Company identity, channel state, and content execution stay in one operating layer.",
  },
] as const;

export function AuthPage({ mode }: AuthPageProps) {
  const content = authContent[mode];
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    const formData = new FormData(event.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        const companyName = formData.get("companyName") as string;
        await register(email, password, companyName);
      }
      navigate("/");
    } catch (err) {
      if (err instanceof HttpError && err.error?.message) {
        setError(err.error.message);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-panel">
        <header className="auth-header">
          <Link className="brand" to="/" aria-label="marektflow.ai home">
            <span className="brand-mark" />
            <span className="brand-name">marektflow.ai</span>
          </Link>

          <Link className="auth-return" to="/">
            Back to site
          </Link>
        </header>

        <div className="auth-body">
          <div className="auth-copy reveal">
            <p className="auth-eyebrow">{content.eyebrow}</p>
            <h1 className="auth-title">{content.title}</h1>
            <p className="auth-description">{content.description}</p>
          </div>

          <form className="auth-form reveal reveal-delay-1" onSubmit={handleSubmit}>
            {error ? (
              <div className="auth-error" role="alert">
                {error}
              </div>
            ) : null}

            {mode === "register" ? (
              <label className="auth-field">
                <span>Company name</span>
                <input
                  autoComplete="organization"
                  className="auth-input"
                  name="companyName"
                  placeholder="Acme Studio"
                  required
                  type="text"
                />
              </label>
            ) : null}

            <label className="auth-field">
              <span>Email</span>
              <input
                autoComplete="email"
                className="auth-input"
                name="email"
                placeholder="you@company.com"
                required
                type="email"
              />
            </label>

            <label className="auth-field">
              <div className="auth-field-row">
                <span>Password</span>
                {mode === "login" ? (
                  <a className="auth-mini-link" href="mailto:hello@marektflow.ai">
                    Need access help?
                  </a>
                ) : (
                  <span className="auth-mini-copy">Minimum 8 characters</span>
                )}
              </div>
              <input
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                className="auth-input auth-input-password"
                name="password"
                placeholder="••••••••••"
                required
                type="password"
              />
            </label>

            <button className="button button-primary auth-submit" type="submit" disabled={isLoading}>
              {isLoading ? "Processing..." : content.submitLabel}
            </button>

            <p className="auth-helper">{content.helper}</p>

            <div className="auth-switch">
              <span>{content.altPrompt}</span>
              <Link className="auth-switch-link" to={content.altTo}>
                {content.altLabel}
              </Link>
            </div>
          </form>
        </div>

        <footer className="auth-footer reveal reveal-delay-2">
          {telemetryRows.map((row) => (
            <span key={row}>{row}</span>
          ))}
        </footer>
      </section>

      <aside className="auth-visual">
        <div className="auth-visual-grid" />
        <div className="auth-orbit auth-orbit-one" />
        <div className="auth-orbit auth-orbit-two" />

        <div className="auth-visual-copy">
          <p className="auth-visual-kicker">System access for the automation layer</p>
          <h2>
            Enter the workspace where campaigns and delivery stay in the same frame.
          </h2>

          <div className="auth-visual-points">
            {rightRailPoints.map((point) => (
              <article className="auth-point" key={point.label}>
                <h3>{point.label}</h3>
                <p>{point.body}</p>
              </article>
            ))}
          </div>

          <div className="auth-status">
            <span className="note-label">Operator state</span>
            <strong>{mode === "login" ? "Awaiting credential verification" : "Workspace profile ready for creation"}</strong>
            <span>
              {mode === "login"
                ? "Resume active campaigns and publishing controls."
                : "Create the company account, then connect channels and begin orchestration."}
            </span>
          </div>
        </div>
      </aside>
    </main>
  );
}
