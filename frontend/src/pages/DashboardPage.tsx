import { DashboardView } from "@/features/dashboard/components/DashboardView";
import { useDashboardQuery } from "@/features/dashboard/hooks/useDashboardQuery";
import { Button } from "@/shared/ui/Button";
import { Card } from "@/shared/ui/Card";
import { SectionState } from "@/shared/ui/SectionState";

export function DashboardPage() {
  const dashboardQuery = useDashboardQuery();

  return (
    <div className="space-y-6">
      <section className="rounded-[2rem] border border-white/10 bg-[linear-gradient(135deg,rgba(8,47,73,0.72),rgba(15,23,42,0.92))] px-6 py-8 shadow-[0_35px_100px_-45px_rgba(8,47,73,0.75)]">
        <p className="text-sm uppercase tracking-[0.28em] text-cyan-200/80">Overview</p>
        <h1 className="mt-4 text-4xl font-semibold text-white">Dashboard</h1>
        <p className="mt-3 max-w-2xl text-sm text-slate-300">
          This starter view is already wired to the backend dashboard endpoint and can expand cleanly into campaigns, posts, and channels.
        </p>
      </section>

      {dashboardQuery.isLoading ? (
        <Card>
          <SectionState
            description="Loading the current dashboard snapshot from the backend."
            title="Fetching dashboard"
          />
        </Card>
      ) : null}

      {dashboardQuery.isError ? (
        <Card>
          <SectionState
            actionLabel="Retry"
            description="The dashboard request failed. Check the backend server and authentication state, then retry."
            onAction={() => void dashboardQuery.refetch()}
            title="Unable to load dashboard"
          />
        </Card>
      ) : null}

      {dashboardQuery.data ? <DashboardView dashboard={dashboardQuery.data} /> : null}

      {dashboardQuery.isSuccess && !dashboardQuery.data ? (
        <Card>
          <SectionState
            description="The backend responded without dashboard data."
            title="No dashboard data"
          />
        </Card>
      ) : null}

      {dashboardQuery.isError ? (
        <div>
          <Button onClick={() => void dashboardQuery.refetch()} variant="ghost">
            Retry request
          </Button>
        </div>
      ) : null}
    </div>
  );
}

