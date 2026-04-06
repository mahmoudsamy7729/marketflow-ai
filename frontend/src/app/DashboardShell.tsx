import { useEffect, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "@/features/auth/hooks/useAuth";

interface DashboardShellNavItem {
  label: string;
  href?: string;
  to?: string;
}

export const dashboardSidebarNavItems: DashboardShellNavItem[] = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Channels", to: "/channels" },
  { label: "Settings", to: "/settings" },
  { label: "Overview", to: "/dashboard#overview" },
  { label: "Queue", to: "/dashboard#queue" },
  { label: "Activity", to: "/dashboard#activity" },
  { label: "Campaign health", to: "/dashboard#health" },
];

export const dashboardSidebarLiveRoute = "GET /dashboard";
export const dashboardSidebarLiveDescription = "Auth-protected operational summary";

interface DashboardShellProps {
  children: ReactNode;
  liveDescription: string;
  liveRoute: string;
  navAriaLabel: string;
  navItems: DashboardShellNavItem[];
}

export function DashboardShell({
  children,
  liveDescription,
  liveRoute,
  navAriaLabel,
  navItems,
}: DashboardShellProps) {
  const { logout, user } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(min-width: 1081px)");

    function handleViewportChange(event: MediaQueryListEvent) {
      if (event.matches) {
        setIsSidebarOpen(false);
      }
    }

    mediaQuery.addEventListener("change", handleViewportChange);

    return () => {
      mediaQuery.removeEventListener("change", handleViewportChange);
    };
  }, []);

  async function handleLogout() {
    await logout();
  }

  const resolvedNavItems = user?.is_admin
    ? [...navItems, { label: "AI Providers", to: "/admin/ai-providers" }]
    : navItems;

  return (
    <main className={`dashboard-shell ${isSidebarOpen ? "is-sidebar-open" : ""}`}>
      <aside className={`dashboard-sidebar ${isSidebarOpen ? "is-open" : ""}`}>
        <div className="dashboard-sidebar-mobilebar">
          <Link aria-label="marektflow.ai home" className="brand" to="/">
            <span className="brand-mark" />
            <span className="brand-name">marektflow.ai</span>
          </Link>

          <button
            aria-controls="dashboard-sidebar-content"
            aria-expanded={isSidebarOpen}
            className="button button-secondary dashboard-sidebar-toggle"
            onClick={() => setIsSidebarOpen((currentValue) => !currentValue)}
            type="button"
          >
            {isSidebarOpen ? "Close menu" : "Open menu"}
          </button>
        </div>

        <div className="dashboard-sidebar-content" id="dashboard-sidebar-content">
          <div className="dashboard-sidebar-top">
            <Link aria-label="marektflow.ai home" className="brand" to="/">
              <span className="brand-mark" />
              <span className="brand-name">marektflow.ai</span>
            </Link>

            <div className="dashboard-sidebar-block">
              <p className="dashboard-sidebar-label">Workspace</p>
              <strong>{user?.company_name ?? "Your company"}</strong>
              <span>{user?.email}</span>
            </div>

            <nav aria-label={navAriaLabel} className="dashboard-nav">
              {resolvedNavItems.map((item) =>
                item.to ? (
                  <Link key={`${item.label}-${item.to}`} onClick={() => setIsSidebarOpen(false)} to={item.to}>
                    {item.label}
                  </Link>
                ) : (
                  <a href={item.href} key={`${item.label}-${item.href}`} onClick={() => setIsSidebarOpen(false)}>
                    {item.label}
                  </a>
                ),
              )}
            </nav>
          </div>

          <div className="dashboard-sidebar-bottom">
            <div className="dashboard-sidebar-block">
              <p className="dashboard-sidebar-label">Live route</p>
              <strong>{liveRoute}</strong>
              <span>{liveDescription}</span>
            </div>

            <button className="button button-secondary dashboard-logout" onClick={() => void handleLogout()} type="button">
              Sign out
            </button>
          </div>
        </div>
      </aside>

      <button
        aria-hidden={!isSidebarOpen}
        className={`dashboard-sidebar-backdrop ${isSidebarOpen ? "is-visible" : ""}`}
        onClick={() => setIsSidebarOpen(false)}
        tabIndex={isSidebarOpen ? 0 : -1}
        type="button"
      />

      <section className="dashboard-main">{children}</section>
    </main>
  );
}
