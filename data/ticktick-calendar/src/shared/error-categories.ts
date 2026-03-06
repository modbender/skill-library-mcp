export type TickTickErrorCategory =
  | "auth_401"
  | "auth_403"
  | "not_found_404"
  | "rate_limit_429"
  | "server_5xx"
  | "network"
  | "validation"
  | "unknown";

export interface TickTickErrorContext {
  category: TickTickErrorCategory;
  message: string;
  status?: number;
  retriable: boolean;
  cause?: unknown;
  responseBody?: unknown;
}

export class TickTickDomainError extends Error {
  readonly category: TickTickErrorCategory;
  readonly status: number | undefined;
  readonly retriable: boolean;
  override readonly cause: unknown;
  readonly responseBody: unknown;

  constructor(context: TickTickErrorContext) {
    super(context.message);
    this.name = "TickTickDomainError";
    this.category = context.category;
    this.status = context.status;
    this.retriable = context.retriable;
    this.cause = context.cause;
    this.responseBody = context.responseBody;
  }
}

export function categorizeHttpStatus(status: number): TickTickErrorCategory {
  if (status === 401) {
    return "auth_401";
  }
  if (status === 403) {
    return "auth_403";
  }
  if (status === 404) {
    return "not_found_404";
  }
  if (status === 429) {
    return "rate_limit_429";
  }
  if (status >= 500 && status <= 599) {
    return "server_5xx";
  }

  return "unknown";
}

export function isRetriableCategory(category: TickTickErrorCategory): boolean {
  return category === "rate_limit_429" || category === "server_5xx" || category === "network";
}
