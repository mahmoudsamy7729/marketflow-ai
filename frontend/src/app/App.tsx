import { RouterProvider } from "react-router-dom";

import "@/app/styles.css";

import { AppProviders } from "@/app/providers/AppProviders";
import { createAppRouter } from "@/app/router/router";

const router = createAppRouter();

export function App() {
  return (
    <AppProviders>
      <RouterProvider router={router} />
    </AppProviders>
  );
}

