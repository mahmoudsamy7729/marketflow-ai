import { useQuery } from "@tanstack/react-query";

import { getDashboard } from "@/features/dashboard/api/dashboardApi";

export function useDashboardQuery() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: getDashboard,
  });
}

