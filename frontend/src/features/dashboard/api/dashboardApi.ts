import { API_ORIGIN, HttpError, getAuthToken } from "@/shared/api/http";
import type { DashboardResponse } from "@/features/dashboard/types/dashboard";

export async function getDashboard(): Promise<DashboardResponse> {
  const token = getAuthToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_ORIGIN}/dashboard`, {
    method: "GET",
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let error: { code: string; message: string; extra?: Record<string, unknown> } | null = null;

    try {
      const body = (await response.json()) as { error?: typeof error };
      error = body.error ?? null;
    } catch {
      error = null;
    }

    throw new HttpError(response.status, error);
  }

  return (await response.json()) as DashboardResponse;
}
