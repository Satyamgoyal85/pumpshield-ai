const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface IndicatorScore {
  name: string;
  score: number;
  max_score: number;
  detail: string;
}

export interface Analysis {
  id: number;
  stock_symbol: string;
  risk_score: number;
  risk_level: "green" | "red";
  explanation: string;
  indicators: IndicatorScore[];
  created_at: string;
}

export interface AnalysisSummary {
  id: number;
  stock_symbol: string;
  risk_score: number;
  risk_level: "green" | "red";
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function setToken(token: string) {
  localStorage.setItem("token", token);
}

export function clearToken() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

export function setUser(user: User) {
  localStorage.setItem("user", JSON.stringify(user));
}

export function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    if (res.status === 401 && typeof window !== "undefined") {
      clearToken();
      window.location.href = "/login";
    }
    throw new ApiError(res.status, body.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  register: (name: string, email: string, password: string) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),

  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  analyze: (symbol: string) =>
    request<Analysis>("/analysis", {
      method: "POST",
      body: JSON.stringify({ symbol }),
    }),

  history: (skip = 0, limit = 20) =>
    request<{ items: AnalysisSummary[]; total: number }>(
      `/analysis/history?skip=${skip}&limit=${limit}`
    ),

  getAnalysis: (id: number) => request<Analysis>(`/analysis/${id}`),
};
