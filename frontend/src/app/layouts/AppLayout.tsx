import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "@/features/auth/hooks/useAuth";
import { Button } from "@/shared/ui/Button";

const navigationItems = [
  {
    label: "Dashboard",
    to: "/dashboard",
  },
  {
    label: "Channels",
    to: "/channels",
  },
];

export function AppLayout() {
  const { logout, user } = useAuth();

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="flex flex-col gap-6 rounded-[2rem] border border-white/10 bg-white/[0.06] p-6 backdrop-blur-md">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-cyan-200/80">Marketoumation</p>
            <h1 className="mt-4 text-2xl font-semibold text-white">Workspace</h1>
            <p className="mt-2 text-sm text-slate-400">
              Manage dashboard insight and connected publishing channels.
            </p>
          </div>

          <nav aria-label="Primary" className="flex flex-col gap-2">
            {navigationItems.map((item) => (
              <NavLink
                className={({ isActive }) =>
                  isActive
                    ? "rounded-2xl bg-cyan-400/15 px-4 py-3 text-sm font-medium text-cyan-100 ring-1 ring-cyan-400/20"
                    : "rounded-2xl px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/[0.08]"
                }
                key={item.to}
                to={item.to}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto rounded-2xl border border-white/10 bg-slate-950/[0.45] p-4">
            <p className="text-sm font-medium text-white">{user?.companyName}</p>
            <p className="mt-1 text-sm text-slate-400">{user?.email}</p>
            <div className="mt-4">
              <Button className="w-full" onClick={() => void logout()} variant="secondary">
                Sign out
              </Button>
            </div>
          </div>
        </aside>

        <main className="min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
