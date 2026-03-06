import { describe, expect, it, vi } from "vitest";
import { TickTickApiClient, TickTickApiError } from "../../src/api/index.js";

interface MockResponse {
  ok: boolean;
  status: number;
  statusText: string;
  headers: { get(name: string): string | null };
  json: () => Promise<unknown>;
  text: () => Promise<string>;
}

function createMockResponse(params: {
  ok: boolean;
  status: number;
  statusText?: string;
  body?: unknown;
  contentType?: string;
  retryAfter?: string;
}): MockResponse {
  const contentType = params.contentType ?? "application/json";
  return {
    ok: params.ok,
    status: params.status,
    statusText: params.statusText ?? "",
    headers: {
      get(name: string) {
        const key = name.toLowerCase();
        if (key === "content-type") {
          return contentType;
        }
        if (key === "retry-after") {
          return params.retryAfter ?? null;
        }
        return null;
      },
    },
    async json() {
      return params.body;
    },
    async text() {
      if (typeof params.body === "string") {
        return params.body;
      }
      return params.body === undefined ? "" : JSON.stringify(params.body);
    },
  };
}

describe("api module", () => {
  it("sends TickTick requests with required authorization header", async () => {
    const fetchMock = vi.fn(async (_url: string, init: { headers: Record<string, string> }) => {
      expect(init.headers.authorization).toBe("Bearer token-123");
      expect(init.headers.accept).toBe("application/json");

      return createMockResponse({
        ok: true,
        status: 200,
        body: { value: 1 },
      });
    });

    const client = new TickTickApiClient({
      baseUrl: "https://api.ticktick.com/open/v1",
      getAccessToken: () => "token-123",
      fetchImplementation: fetchMock,
    });

    await expect(client.get<{ value: number }>("/task")).resolves.toEqual({ value: 1 });
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("retries transient 429 and 5xx failures with backoff", async () => {
    const fetchMock = vi
      .fn<
        (url: string, init: { headers: Record<string, string> }) => Promise<MockResponse>
      >()
      .mockResolvedValueOnce(
        createMockResponse({
          ok: false,
          status: 429,
          statusText: "Too Many Requests",
          body: { error: "rate_limited" },
          retryAfter: "0",
        })
      )
      .mockResolvedValueOnce(
        createMockResponse({
          ok: false,
          status: 502,
          statusText: "Bad Gateway",
          body: { error: "upstream" },
        })
      )
      .mockResolvedValueOnce(
        createMockResponse({
          ok: true,
          status: 200,
          body: { value: 3 },
        })
      );

    const client = new TickTickApiClient({
      baseUrl: "https://api.ticktick.com/open/v1",
      getAccessToken: () => "token-123",
      fetchImplementation: fetchMock,
      maxRetries: 3,
      retryBaseDelayMs: 1,
      timeoutMs: 500,
    });

    await expect(client.get<{ value: number }>("/task")).resolves.toEqual({ value: 3 });
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it("normalizes non-standard error responses into typed errors", async () => {
    const fetchMock = vi.fn(async () =>
      createMockResponse({
        ok: false,
        status: 403,
        statusText: "Forbidden",
        body: "forbidden",
        contentType: "text/plain",
      })
    );

    const client = new TickTickApiClient({
      baseUrl: "https://api.ticktick.com/open/v1",
      getAccessToken: () => "token-123",
      fetchImplementation: fetchMock,
      maxRetries: 0,
    });

    await expect(client.get("/task")).rejects.toBeInstanceOf(TickTickApiError);
    await expect(client.get("/task")).rejects.toMatchObject({
      status: 403,
      retryable: false,
      body: "forbidden",
    });
  });
});
