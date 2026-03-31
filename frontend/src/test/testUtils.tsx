import { render } from "@testing-library/react";
import { RouterProvider } from "react-router-dom";
import { vi } from "vitest";

import { AppProviders } from "@/app/providers/AppProviders";
import { createTestRouter } from "@/app/router/router";

type MockResponseFactory = () => Response | Promise<Response>;

interface RouteHandler {
  method?: string;
  path: string;
  response: Response | MockResponseFactory;
}

export function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init.headers ?? {}),
    },
  });
}

function resolveRequestUrl(input: string | URL | Request) {
  if (typeof input === "string") {
    return input;
  }

  if (input instanceof URL) {
    return input.toString();
  }

  return input.url;
}

export function createRouteHandlers(routes: RouteHandler[]) {
  return vi.spyOn(global, "fetch").mockImplementation(async (input, init) => {
    const url = new URL(resolveRequestUrl(input));
    const method = (init?.method ?? "GET").toUpperCase();
    const route = routes.find(
      (candidate) =>
        candidate.path === url.pathname &&
        (candidate.method ?? "GET").toUpperCase() === method,
    );

    if (!route) {
      throw new Error(`Unhandled request: ${method} ${url.pathname}`);
    }

    return typeof route.response === "function"
      ? await route.response()
      : route.response;
  });
}

export function renderApp(initialEntries: string[] = ["/"]) {
  const router = createTestRouter(initialEntries);

  return {
    router,
    ...render(
      <AppProviders>
        <RouterProvider router={router} />
      </AppProviders>,
    ),
  };
}
