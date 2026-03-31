import { apiRequest } from "@/shared/api/http";

import type { AuthSession, LoginInput, RegisterInput, User } from "@/features/auth/types/auth";

interface UserDto {
  id: string;
  email: string;
  company_name: string;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

interface AuthSessionDto {
  access_token: string;
  user: UserDto;
}

interface MessageResponseDto {
  message: string;
}

function mapUser(user: UserDto): User {
  return {
    id: user.id,
    email: user.email,
    companyName: user.company_name,
    createdAt: user.created_at,
    updatedAt: user.updated_at,
    deletedAt: user.deleted_at,
  };
}

function mapSession(session: AuthSessionDto): AuthSession {
  return {
    accessToken: session.access_token,
    user: mapUser(session.user),
  };
}

export async function loginUser(payload: LoginInput) {
  const response = await apiRequest<AuthSessionDto>("/api/auth/login", {
    method: "POST",
    body: payload,
    credentials: "include",
  });

  return mapSession(response);
}

export async function registerUser(payload: RegisterInput) {
  const response = await apiRequest<AuthSessionDto>("/api/auth/register", {
    method: "POST",
    body: payload,
    credentials: "include",
  });

  return mapSession(response);
}

export async function refreshSession() {
  const response = await apiRequest<AuthSessionDto>("/api/auth/refresh", {
    method: "POST",
    credentials: "include",
  });

  return mapSession(response);
}

export async function getCurrentUser() {
  const response = await apiRequest<UserDto>("/api/auth/me", {
    method: "GET",
    auth: true,
  });

  return mapUser(response);
}

export async function logoutUser() {
  return apiRequest<MessageResponseDto>("/api/auth/logout", {
    method: "POST",
    credentials: "include",
  });
}

