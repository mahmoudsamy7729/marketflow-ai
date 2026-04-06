export interface User {
  id: string;
  email: string;
  company_name: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface AuthSession {
  access_token: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  company_name: string;
}

export interface MessageResponse {
  message: string;
}
