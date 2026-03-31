export interface User {
  id: string;
  email: string;
  companyName: string;
  createdAt: string;
  updatedAt: string;
  deletedAt: string | null;
}

export interface AuthSession {
  accessToken: string;
  user: User;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput extends LoginInput {
  companyName: string;
}

