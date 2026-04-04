export const API_ORIGIN = "http://localhost:8000";
const API_BASE_URL = `${API_ORIGIN}/api`;

let authToken: string | null = null;

export function setAuthToken(token: string | null): void {
  authToken = token;
}

export function getAuthToken(): string | null {
  return authToken;
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
}

interface ApiError {
  code: string;
  message: string;
  extra?: Record<string, unknown>;
}

export class HttpError extends Error {
  status: number;
  error: ApiError | null;

  constructor(status: number, error: ApiError | null) {
    super(error?.message || `HTTP Error: ${status}`);
    this.name = "HttpError";
    this.status = status;
    this.error = error;
  }
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers,
    credentials: "include",
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let error: ApiError | null = null;
    try {
      const errorBody = await response.json();
      error = errorBody.error || null;
    } catch {
      // Response body is not JSON
    }
    throw new HttpError(response.status, error);
  }

  return response.json();
}

export const http = {
  get: <T>(endpoint: string): Promise<T> => request<T>(endpoint, { method: "GET" }),
  post: <T>(endpoint: string, body?: unknown): Promise<T> =>
    request<T>(endpoint, { method: "POST", body }),
  put: <T>(endpoint: string, body?: unknown): Promise<T> =>
    request<T>(endpoint, { method: "PUT", body }),
  patch: <T>(endpoint: string, body?: unknown): Promise<T> =>
    request<T>(endpoint, { method: "PATCH", body }),
  delete: <T>(endpoint: string): Promise<T> => request<T>(endpoint, { method: "DELETE" }),
};
