import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6 py-12">
      <div className="grid w-full max-w-6xl gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="hidden rounded-[2rem] border border-white/10 bg-[linear-gradient(135deg,rgba(15,23,42,0.8),rgba(8,47,73,0.9))] p-10 lg:block">
          <p className="text-sm font-medium uppercase tracking-[0.3em] text-cyan-200/90">
            Marketoumation
          </p>
          <h2 className="mt-6 max-w-md text-5xl font-semibold leading-tight text-white">
            Clean control over automated marketing execution.
          </h2>
          <p className="mt-6 max-w-lg text-base text-slate-300">
            Start with auth, restore the session on refresh, and keep the frontend ready for campaigns, content planning, and publishing workflows.
          </p>
        </section>

        <section className="rounded-[2rem] border border-white/10 bg-slate-950/70 p-8 shadow-[0_35px_90px_-45px_rgba(15,23,42,0.85)] backdrop-blur-xl sm:p-10">
          <Outlet />
        </section>
      </div>
    </main>
  );
}

