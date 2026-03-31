import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "@/features/auth/hooks/useAuth";
import { Button } from "@/shared/ui/Button";

export function AppLayout() {
  const { logout, user } = useAuth();

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-8">
        <header className="flex flex-col gap-5 rounded-[2rem] border border-white/10 bg-white/[0.06] px-6 py-5 backdrop-blur-md sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-cyan-200/80">Marketoumation</p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <NavLink
                className={({ isActive }) =>
                  isActive
                    ? "rounded-full bg-cyan-400/15 px-4 py-2 text-sm font-medium text-cyan-100 ring-1 ring-cyan-400/20"
                    : "rounded-full px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/[0.08]"
                }
                to="/dashboard"
              >
                Dashboard
              </NavLink>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-white">{user?.companyName}</p>
              <p className="text-sm text-slate-400">{user?.email}</p>
            </div>
            <Button onClick={() => void logout()} variant="secondary">
              Sign out
            </Button>
          </div>
        </header>

        <Outlet />
      </div>
    </div>
  );
}

