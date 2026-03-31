import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="max-w-md rounded-[2rem] border border-white/10 bg-slate-950/70 p-8 text-center shadow-[0_30px_80px_-45px_rgba(15,23,42,0.85)] backdrop-blur-xl">
        <p className="text-sm uppercase tracking-[0.25em] text-cyan-200/70">404</p>
        <h1 className="mt-4 text-3xl font-semibold text-white">Page not found</h1>
        <p className="mt-3 text-sm text-slate-400">
          The page you requested does not exist in this frontend scaffold.
        </p>
        <Link className="mt-6 inline-flex rounded-xl bg-white/[0.08] px-4 py-2 text-sm font-semibold text-white ring-1 ring-white/[0.15] hover:bg-white/[0.12]" to="/dashboard">
          Go to dashboard
        </Link>
      </div>
    </main>
  );
}

