import type { AuthSession, LoginRequest, RegisterRequest, User, MessageResponse } from "../types/auth";
import { http } from "@/shared/api/http";
import { setAuthToken } from "@/shared/api/http";

export async function register(payload: RegisterRequest): Promise<AuthSession> {
  const response = await http.post<AuthSession>("/auth/register", payload);
  setAuthToken(response.access_token);
  return response;
}

export async function login(payload: LoginRequest): Promise<AuthSession> {
  const response = await http.post<AuthSession>("/auth/login", payload);
  setAuthToken(response.access_token);
  return response;
}

export async function logout(): Promise<MessageResponse> {
  const response = await http.post<MessageResponse>("/auth/logout");
  setAuthToken(null);
  return response;
}

export async function getMe(): Promise<User> {
  return http.get<User>("/auth/me");
}

export async function refreshSession(): Promise<AuthSession> {
  const response = await http.post<AuthSession>("/auth/refresh");
  setAuthToken(response.access_token);
  return response;
}