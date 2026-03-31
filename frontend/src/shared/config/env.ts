import { z } from "zod";

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().url(),
});

const envInput = {
  VITE_API_BASE_URL: String(
    import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000",
  ),
};

const parsedEnv = envSchema.parse(envInput);

export const env = {
  apiBaseUrl: parsedEnv.VITE_API_BASE_URL.replace(/\/$/, ""),
};
