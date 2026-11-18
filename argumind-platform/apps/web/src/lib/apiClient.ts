import { ProblemDetailsSchema, type ProblemDetails } from "@argumind/shared-schemas";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ArgumindApiError extends Error {
  public readonly status: number;
  public readonly code: string;
  public readonly traceId: string;

  constructor(problem: ProblemDetails) {
    super(problem.detail);
    this.name = "ArgumindApiError";
    this.status = problem.status;
    this.code = problem.code;
    this.traceId = problem.trace_id;
  }
}

function getCookieValue(name: string): string {
  if (typeof document === "undefined") return "";
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.split("=")[1] ?? "") : "";
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers);
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrf = getCookieValue("argumind_csrf_token");
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    credentials: "include",
  });

  if (!res.ok) {
    const raw: unknown = await res.json().catch(() => null);
    const parsed = ProblemDetailsSchema.safeParse(raw);
    if (parsed.success) {
      throw new ArgumindApiError(parsed.data);
    }
    throw new ArgumindApiError({
      type: "https://argumind.id/errors/unknown",
      title: "Request Failed",
      status: res.status,
      code: "ERR_UNKNOWN",
      detail: `Permintaan gagal dengan status ${res.status}.`,
      trace_id: "unknown",
    });
  }
  return (await res.json()) as T;
}
