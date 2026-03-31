import { getAccessToken } from "@/features/auth/lib/session";
import { env } from "@/shared/config/env";

type PrimitiveBody = BodyInit | null | undefined;

interface BackendErrorPayload {
  error?: {
    code?: string;
    message?: string;
    extra?: Record<string, unknown>;
  };
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  auth?: boolean;
  body?: PrimitiveBody | object;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
    readonly extra?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function isBodyInit(value: unknown): value is BodyInit {
  return (
    value instanceof FormData ||
    value instanceof Blob ||
    value instanceof URLSearchParams ||
    typeof value === "string" ||
    value instanceof ArrayBuffer ||
    ArrayBuffer.isView(value)
  );
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { auth = false, body, headers, ...requestInit } = options;
  const requestHeaders = new Headers(headers);

  if (auth) {
    const accessToken = getAccessToken();
    if (accessToken) {
      requestHeaders.set("Authorization", `Bearer ${accessToken}`);
    }
  }

  let requestBody: BodyInit | undefined;
  if (body !== undefined && body !== null) {
    if (isBodyInit(body)) {
      requestBody = body;
    } else {
      requestHeaders.set("Content-Type", "application/json");
      requestBody = JSON.stringify(body);
    }
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    ...requestInit,
    headers: requestHeaders,
    body: requestBody,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const hasJsonBody = contentType.includes("application/json");
  const responsePayload = hasJsonBody
    ? ((await response.json()) as BackendErrorPayload | T)
    : null;

  if (!response.ok) {
    const errorPayload = responsePayload as BackendErrorPayload | null;
    throw new ApiError(
      errorPayload?.error?.message ?? "The request failed.",
      response.status,
      errorPayload?.error?.code ?? "request_failed",
      errorPayload?.error?.extra,
    );
  }

  return responsePayload as T;
}
