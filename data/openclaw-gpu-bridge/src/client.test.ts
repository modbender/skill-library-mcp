import { GpuBridgeClient, InputValidationError } from "./client";

describe("GpuBridgeClient multi-host", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  test("supports v0.1 fallback config via serviceUrl", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok", device: "cuda" }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({ serviceUrl: "http://legacy:8765" });
    const health = await client.health();

    expect(health.status).toBe("ok");
    expect(fetchMock.mock.calls.some((c) => c[0] === "http://legacy:8765/health")).toBe(true);
  });

  test("fails over to next host when first host is down", async () => {
    const fetchMock = jest.fn(async (url: string) => {
      if (url === "http://host-a:8765/health") {
        throw new Error("ECONNREFUSED");
      }
      if (url === "http://host-b:8765/health") {
        return { ok: true, json: async () => ({ status: "ok", device: "cuda" }) };
      }
      return { ok: true, json: async () => ({ status: "ok", device: "cuda" }) };
    });

    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      hosts: [{ url: "http://host-a:8765" }, { url: "http://host-b:8765" }],
    });

    const health = await client.health();

    expect(health.status).toBe("ok");
    expect(fetchMock.mock.calls.some((c) => c[0] === "http://host-a:8765/health")).toBe(true);
    expect(fetchMock.mock.calls.some((c) => c[0] === "http://host-b:8765/health")).toBe(true);
  });

  test("least-busy selects host with lower VRAM utilization", async () => {
    const fetchMock = jest.fn(async (url: string) => {
      if (url === "http://host-a:8765/info") {
        return {
          ok: true,
          json: async () => ({ vram_total_mb: 1000, vram_used_mb: 900 }),
        };
      }

      if (url === "http://host-b:8765/info") {
        return {
          ok: true,
          json: async () => ({ vram_total_mb: 1000, vram_used_mb: 200 }),
        };
      }

      if (url === "http://host-b:8765/embed") {
        return {
          ok: true,
          json: async () => ({ embeddings: [[1, 2]], model: "all-MiniLM-L6-v2", dimensions: 2 }),
        };
      }

      return {
        ok: true,
        json: async () => ({ status: "ok", device: "cuda" }),
      };
    });

    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      hosts: [{ url: "http://host-a:8765" }, { url: "http://host-b:8765" }],
      loadBalancing: "least-busy",
    });

    const result = await client.embed({ texts: ["hello"] });

    expect(result.dimensions).toBe(2);
    expect(fetchMock).toHaveBeenCalledWith("http://host-b:8765/embed", expect.any(Object));
  });
});

describe("GpuBridgeClient input validation", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  test("rejects embed batch exceeding maxBatchSize", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok", device: "cuda" }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      serviceUrl: "http://gpu:8765",
      limits: { maxBatchSize: 5 },
    });

    await expect(
      client.embed({ texts: Array(10).fill("hello") })
    ).rejects.toThrow(InputValidationError);

    await expect(
      client.embed({ texts: Array(10).fill("hello") })
    ).rejects.toThrow("texts array length 10 exceeds max batch size of 5");
  });

  test("rejects bertscore batch exceeding maxBatchSize", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok", device: "cuda" }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      serviceUrl: "http://gpu:8765",
      limits: { maxBatchSize: 3 },
    });

    await expect(
      client.bertscore({
        candidates: Array(5).fill("candidate"),
        references: Array(5).fill("reference"),
      })
    ).rejects.toThrow(InputValidationError);

    await expect(
      client.bertscore({
        candidates: Array(5).fill("candidate"),
        references: Array(5).fill("reference"),
      })
    ).rejects.toThrow("candidates array length 5 exceeds max batch size of 3");
  });

  test("rejects text exceeding maxTextLength", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ok", device: "cuda" }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      serviceUrl: "http://gpu:8765",
      limits: { maxTextLength: 50 },
    });

    const longText = "x".repeat(100);
    await expect(
      client.embed({ texts: [longText] })
    ).rejects.toThrow(InputValidationError);

    await expect(
      client.embed({ texts: [longText] })
    ).rejects.toThrow("texts[0] length 100 exceeds max text length of 50");
  });

  test("allows requests within configured limits", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ embeddings: [[1, 2]], model: "all-MiniLM-L6-v2", dimensions: 2 }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({
      serviceUrl: "http://gpu:8765",
      limits: { maxBatchSize: 5, maxTextLength: 100 },
    });

    const result = await client.embed({ texts: ["hello", "world"] });
    expect(result.dimensions).toBe(2);
  });

  test("uses default limits (100 items, 10000 chars) when not configured", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ embeddings: [[1]], model: "all-MiniLM-L6-v2", dimensions: 1 }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({ serviceUrl: "http://gpu:8765" });

    // 100 items should be fine with default limit
    const result = await client.embed({ texts: Array(100).fill("ok") });
    expect(result.dimensions).toBe(1);

    // 101 items should fail with default limit
    await expect(
      client.embed({ texts: Array(101).fill("ok") })
    ).rejects.toThrow("texts array length 101 exceeds max batch size of 100");
  });
});

describe("GpuBridgeClient Retry-After on 503", () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  test("retries on 503 with Retry-After header and succeeds", async () => {
    let embedCallCount = 0;
    const fetchMock = jest.fn(async (url: string, _init?: RequestInit) => {
      if ((url as string).endsWith("/health")) {
        return { ok: true, json: async () => ({ status: "ok", device: "cuda" }) };
      }
      embedCallCount += 1;
      if (embedCallCount <= 1) {
        return {
          ok: false,
          status: 503,
          headers: { get: (key: string) => (key === "Retry-After" ? "1" : null) },
          text: async () => "GPU busy",
        };
      }
      return {
        ok: true,
        status: 200,
        headers: { get: () => null },
        json: async () => ({ embeddings: [[1, 2]], model: "all-MiniLM-L6-v2", dimensions: 2 }),
      };
    });

    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({ serviceUrl: "http://gpu:8765" });

    const result = await client.embed({ texts: ["hello"] });
    expect(result.dimensions).toBe(2);

    // Should have been called at least twice for /embed (once 503, once success)
    const embedCalls = fetchMock.mock.calls.filter((c) =>
      (c[0] as string).endsWith("/embed")
    );
    expect(embedCalls.length).toBe(2);
  });

  test("marks host unhealthy after exhausting 503 retries", async () => {
    const fetchMock = jest.fn(async (url: string, _init?: RequestInit) => {
      if ((url as string).endsWith("/health")) {
        return { ok: true, json: async () => ({ status: "ok", device: "cuda" }) };
      }
      return {
        ok: false,
        status: 503,
        headers: { get: (key: string) => (key === "Retry-After" ? "1" : null) },
        text: async () => "GPU busy",
      };
    });

    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({ serviceUrl: "http://gpu:8765" });

    await expect(client.embed({ texts: ["hello"] })).rejects.toThrow(
      /returned 503/
    );
  });

  test("does not mark host unhealthy on first 503 when Retry-After is present", async () => {
    let embedCallCount = 0;
    const fetchMock = jest.fn(async (url: string, _init?: RequestInit) => {
      if ((url as string).endsWith("/health")) {
        return { ok: true, json: async () => ({ status: "ok", device: "cuda" }) };
      }
      embedCallCount += 1;
      if (embedCallCount === 1) {
        return {
          ok: false,
          status: 503,
          headers: { get: (key: string) => (key === "Retry-After" ? "1" : null) },
          text: async () => "GPU busy",
        };
      }
      return {
        ok: true,
        status: 200,
        headers: { get: () => null },
        json: async () => ({ embeddings: [[1]], model: "test", dimensions: 1 }),
      };
    });

    global.fetch = fetchMock as unknown as typeof fetch;

    const client = new GpuBridgeClient({ serviceUrl: "http://gpu:8765" });

    // This should succeed on the retry, meaning the host was NOT marked permanently dead
    const result = await client.embed({ texts: ["hello"] });
    expect(result.dimensions).toBe(1);
  });
});
