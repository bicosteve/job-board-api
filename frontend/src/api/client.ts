export function getApiBase(): string {
  const fromEnv = import.meta.env.VITE_API_URL?.trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  if (import.meta.env.DEV) return "/v0/api";
  return "http://127.0.0.1:5005/v0/api";
}

type Json = Record<string, unknown> | unknown[];

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function parseErrorMessage(body: unknown, status: number): string {
  if (body && typeof body === "object" && !Array.isArray(body)) {
    const o = body as Record<string, unknown>;
    const keys = [
      "error",
      "msg",
      "message",
      "credentials_error",
      "validation_error",
      "db_error",
      "user_error",
      "generic_error",
    ];
    for (const k of keys) {
      const v = o[k];
      if (typeof v === "string" && v) return v;
      if (v && typeof v === "object") return JSON.stringify(v);
    }
  }
  return `Request failed (${status})`;
}

export async function apiRequest<T = Json>(
  path: string,
  init: RequestInit & { token?: string | null } = {}
): Promise<T> {
  const base = getApiBase();
  const url = path.startsWith("http") ? path : `${base}${path.startsWith("/") ? "" : "/"}${path}`;
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  if (init.token) {
    headers.set("Authorization", `Bearer ${init.token}`);
  }

  const { token: _omit, ...rest } = init;
  const res = await fetch(url, { ...rest, headers });

  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text) as unknown;
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    throw new ApiError(parseErrorMessage(data, res.status), res.status, data);
  }

  return data as T;
}
