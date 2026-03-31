import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "@/features/auth/hooks/useAuth";

function FullScreenStatus({ title }: { title: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center px-6 text-center text-sm text-slate-300">
      {title}
    </div>
  );
}

export function RequireAuth() {
  const { isAuthenticated, status } = useAuth();
  const location = useLocation();

  if (status === "loading") {
    return <FullScreenStatus title="Restoring session..." />;
  }

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  return <Outlet />;
}

export function PublicOnlyRoute() {
  const { isAuthenticated, status } = useAuth();

  if (status === "loading") {
    return <FullScreenStatus title="Checking session..." />;
  }

  if (isAuthenticated) {
    return <Navigate replace to="/dashboard" />;
  }

  return <Outlet />;
}
