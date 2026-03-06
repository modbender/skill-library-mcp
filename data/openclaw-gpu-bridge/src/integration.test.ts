// Integration tests for multi-host GPU Bridge using real HTTP servers.
// These tests spin up multiple HTTP servers to simulate GPU service hosts,
// then verify the TypeScript client's orchestration logic end-to-end
// (round-robin, least-busy, failover, auth, /status).

import * as http from "http";
import { GpuBridgeClient } from "./client";

// --- Helpers ---

interface MockGpuHost {
  server: http.Server;
  port: number;
  url: string;
  requestLog: Array<{ method: string; path: string; headers: Record<string, string | string[] | undefined> }>;
  close: () => Promise<void>;
}

interface MockHostOptions {
  port: number;
  deviceName?: string;
  vramTotal?: number;
  vramUsed?: number;
  apiKey?: string;
  /** If true, server rejects connections (simulates dead host) */
  dead?: boolean;
  /** If set, /embed and /bertscore return 503 for the first N calls */
  busy503Count?: number;
}

function createMockGpuHost(opts: MockHostOptions): Promise<MockGpuHost> {
  const requestLog: MockGpuHost["requestLog"] = [];
  let busy503Remaining = opts.busy503Count ?? 0;

  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      requestLog.push({
        method: req.method ?? "GET",
        path: req.url ?? "/",
        headers: req.headers as Record<string, string | string[] | undefined>,
      });

      // Auth check
      if (opts.apiKey && req.url !== "/health") {
        const provided = req.headers["x-api-key"];
        if (provided !== opts.apiKey) {
          res.writeHead(401, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ detail: "Unauthorized" }));
          return;
        }
      }

      const sendJson = (status: number, body: unknown, extraHeaders?: Record<string, string>) => {
        res.writeHead(status, { "Content-Type": "application/json", ...extraHeaders });
        res.end(JSON.stringify(body));
      };

      // 503 simulation for compute endpoints
      if (busy503Remaining > 0 && (req.url === "/embed" || req.url === "/bertscore")) {
        busy503Remaining -= 1;
        sendJson(503, { detail: "GPU busy" }, { "Retry-After": "1" });
        return;
      }

      if (req.url === "/health") {
        sendJson(200, { status: "ok", device: "cuda" });
      } else if (req.url === "/info") {
        sendJson(200, {
          device: "cuda",
          device_name: opts.deviceName ?? "Mock GPU",
          vram_total_mb: opts.vramTotal ?? 8000,
          vram_used_mb: opts.vramUsed ?? 2000,
          pytorch_version: "2.5.0",
          cuda_version: "12.4",
          loaded_models: ["all-MiniLM-L6-v2", "microsoft/deberta-xlarge-mnli"],
        });
      } else if (req.url === "/status") {
        sendJson(200, {
          queue: { max_concurrent: 2, in_flight: 0, available_slots: 2, waiting_estimate: 0 },
          active_jobs: [],
        });
      } else if (req.url === "/embed" && req.method === "POST") {
        let body = "";
        req.on("data", (chunk) => { body += chunk; });
        req.on("end", () => {
          const parsed = JSON.parse(body);
          const dim = 384;
          const embeddings = parsed.texts.map(() => Array(dim).fill(0.1));
          sendJson(200, {
            embeddings,
            model: parsed.model ?? "all-MiniLM-L6-v2",
            dimensions: dim,
          });
        });
      } else if (req.url === "/bertscore" && req.method === "POST") {
        let body = "";
        req.on("data", (chunk) => { body += chunk; });
        req.on("end", () => {
          const parsed = JSON.parse(body);
          const count = parsed.candidates.length;
          sendJson(200, {
            precision: Array(count).fill(0.95),
            recall: Array(count).fill(0.93),
            f1: Array(count).fill(0.94),
            model: parsed.model_type ?? "microsoft/deberta-xlarge-mnli",
          });
        });
      } else {
        res.writeHead(404);
        res.end("Not found");
      }
    });

    if (opts.dead) {
      // Don't actually listen - resolve with a server that immediately errors
      const closedServer = http.createServer();
      resolve({
        server: closedServer,
        port: opts.port,
        url: `http://127.0.0.1:${opts.port}`,
        requestLog,
        close: () => Promise.resolve(),
      });
      return;
    }

    server.listen(opts.port, "127.0.0.1", () => {
      resolve({
        server,
        port: opts.port,
        url: `http://127.0.0.1:${opts.port}`,
        requestLog,
        close: () => new Promise<void>((r) => server.close(() => r())),
      });
    });

    server.on("error", reject);
  });
}

// Use high ports unlikely to conflict
const PORT_A = 18701;
const PORT_B = 18702;
const PORT_C = 18703;

// --- Tests ---

describe("Integration: multi-host round-robin", () => {
  let hostA: MockGpuHost;
  let hostB: MockGpuHost;

  beforeAll(async () => {
    hostA = await createMockGpuHost({ port: PORT_A, deviceName: "RTX 3090 (A)" });
    hostB = await createMockGpuHost({ port: PORT_B, deviceName: "RTX 4090 (B)" });
  });

  afterAll(async () => {
    await hostA.close();
    await hostB.close();
  });

  test("distributes embed requests across hosts via round-robin", async () => {
    const client = new GpuBridgeClient({
      hosts: [{ url: hostA.url }, { url: hostB.url }],
      loadBalancing: "round-robin",
      healthCheckIntervalSeconds: 600,
    });

    // Clear logs from health checks triggered by constructor
    await new Promise((r) => setTimeout(r, 200));
    hostA.requestLog.length = 0;
    hostB.requestLog.length = 0;

    // Send 4 embed requests
    for (let i = 0; i < 4; i += 1) {
      await client.embed({ texts: [`request-${i}`] });
    }

    const embedA = hostA.requestLog.filter((r) => r.path === "/embed");
    const embedB = hostB.requestLog.filter((r) => r.path === "/embed");

    // Round-robin should distribute evenly: 2 each
    expect(embedA.length).toBe(2);
    expect(embedB.length).toBe(2);
  });
});

describe("Integration: multi-host least-busy", () => {
  let hostA: MockGpuHost;
  let hostB: MockGpuHost;

  beforeAll(async () => {
    // Host A: high VRAM usage (7500/8000 = 93.75%)
    hostA = await createMockGpuHost({ port: PORT_A, deviceName: "RTX 3090 (busy)", vramTotal: 8000, vramUsed: 7500 });
    // Host B: low VRAM usage (1000/24000 = 4.2%)
    hostB = await createMockGpuHost({ port: PORT_B, deviceName: "RTX 4090 (idle)", vramTotal: 24000, vramUsed: 1000 });
  });

  afterAll(async () => {
    await hostA.close();
    await hostB.close();
  });

  test("selects the host with lower VRAM utilization", async () => {
    const client = new GpuBridgeClient({
      hosts: [{ url: hostA.url }, { url: hostB.url }],
      loadBalancing: "least-busy",
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));
    hostA.requestLog.length = 0;
    hostB.requestLog.length = 0;

    const result = await client.embed({ texts: ["hello world"] });

    expect(result.dimensions).toBe(384);
    expect(result.model).toBe("all-MiniLM-L6-v2");

    // Embed request should go to host B (lower VRAM usage)
    const embedB = hostB.requestLog.filter((r) => r.path === "/embed");
    expect(embedB.length).toBe(1);
  });
});

describe("Integration: failover on host death", () => {
  let hostB: MockGpuHost;

  beforeAll(async () => {
    // Host A is dead (port not listening)
    hostB = await createMockGpuHost({ port: PORT_B, deviceName: "RTX 4090 (alive)" });
  });

  afterAll(async () => {
    await hostB.close();
  });

  test("fails over from dead host to healthy host", async () => {
    const client = new GpuBridgeClient({
      hosts: [
        { url: `http://127.0.0.1:${PORT_A}`, name: "dead-host" },
        { url: hostB.url, name: "alive-host" },
      ],
      loadBalancing: "round-robin",
      healthCheckIntervalSeconds: 600,
      timeout: 3,
    });

    // Wait for initial health checks to mark host A as unhealthy
    await new Promise((r) => setTimeout(r, 500));

    const result = await client.embed({ texts: ["failover test"] });

    expect(result.dimensions).toBe(384);

    // Host B should have received the embed request
    const embedB = hostB.requestLog.filter((r) => r.path === "/embed");
    expect(embedB.length).toBeGreaterThanOrEqual(1);
  });
});

describe("Integration: X-API-Key authentication", () => {
  let hostA: MockGpuHost;
  let hostB: MockGpuHost;

  beforeAll(async () => {
    hostA = await createMockGpuHost({ port: PORT_A, apiKey: "secret-key-A" });
    hostB = await createMockGpuHost({ port: PORT_B, apiKey: "secret-key-B" });
  });

  afterAll(async () => {
    await hostA.close();
    await hostB.close();
  });

  test("sends correct per-host API keys", async () => {
    const client = new GpuBridgeClient({
      hosts: [
        { url: hostA.url, apiKey: "secret-key-A" },
        { url: hostB.url, apiKey: "secret-key-B" },
      ],
      loadBalancing: "round-robin",
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));
    hostA.requestLog.length = 0;
    hostB.requestLog.length = 0;

    // Send 2 requests - one should go to each host
    await client.embed({ texts: ["auth-test-1"] });
    await client.embed({ texts: ["auth-test-2"] });

    // Both should succeed (correct keys), verify auth headers
    const embedA = hostA.requestLog.filter((r) => r.path === "/embed");
    const embedB = hostB.requestLog.filter((r) => r.path === "/embed");

    expect(embedA.length).toBe(1);
    expect(embedB.length).toBe(1);
    expect(embedA[0].headers["x-api-key"]).toBe("secret-key-A");
    expect(embedB[0].headers["x-api-key"]).toBe("secret-key-B");
  });

  test("rejects requests with wrong API key via failover error", async () => {
    const client = new GpuBridgeClient({
      hosts: [
        { url: hostA.url, apiKey: "wrong-key" },
      ],
      loadBalancing: "round-robin",
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));

    await expect(client.embed({ texts: ["should-fail"] })).rejects.toThrow(/401/);
  });
});

describe("Integration: /status endpoint", () => {
  let hostA: MockGpuHost;

  beforeAll(async () => {
    hostA = await createMockGpuHost({ port: PORT_A });
  });

  afterAll(async () => {
    await hostA.close();
  });

  test("returns queue status from real HTTP server", async () => {
    const client = new GpuBridgeClient({
      hosts: [{ url: hostA.url }],
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));

    const status = await client.status();

    expect(status.queue.max_concurrent).toBe(2);
    expect(status.queue.in_flight).toBe(0);
    expect(status.queue.available_slots).toBe(2);
    expect(status.active_jobs).toEqual([]);
  });
});

describe("Integration: bertscore end-to-end", () => {
  let hostA: MockGpuHost;

  beforeAll(async () => {
    hostA = await createMockGpuHost({ port: PORT_A });
  });

  afterAll(async () => {
    await hostA.close();
  });

  test("sends and receives BERTScore results over HTTP", async () => {
    const client = new GpuBridgeClient({
      hosts: [{ url: hostA.url }],
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));

    const result = await client.bertscore({
      candidates: ["The cat sat on the mat"],
      references: ["A cat was sitting on a mat"],
    });

    expect(result.f1).toHaveLength(1);
    expect(result.precision).toHaveLength(1);
    expect(result.recall).toHaveLength(1);
    expect(result.f1[0]).toBeCloseTo(0.94, 1);
    expect(result.model).toBe("microsoft/deberta-xlarge-mnli");
  });
});

describe("Integration: 503 retry with real HTTP", () => {
  let hostA: MockGpuHost;

  beforeAll(async () => {
    // First 2 embed/bertscore calls return 503, then succeed
    hostA = await createMockGpuHost({ port: PORT_A, busy503Count: 2 });
  });

  afterAll(async () => {
    await hostA.close();
  });

  test("retries 503 responses and eventually succeeds", async () => {
    const client = new GpuBridgeClient({
      hosts: [{ url: hostA.url }],
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));

    const result = await client.embed({ texts: ["retry-test"] });

    expect(result.dimensions).toBe(384);

    // Server should have received 3 embed calls (2 x 503, 1 x 200)
    const embedCalls = hostA.requestLog.filter((r) => r.path === "/embed");
    expect(embedCalls.length).toBe(3);
  });
});

describe("Integration: health check", () => {
  let hostA: MockGpuHost;

  beforeAll(async () => {
    hostA = await createMockGpuHost({ port: PORT_A });
  });

  afterAll(async () => {
    await hostA.close();
  });

  test("health endpoint returns ok over real HTTP", async () => {
    const client = new GpuBridgeClient({
      hosts: [{ url: hostA.url }],
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));

    const health = await client.health();

    expect(health.status).toBe("ok");
    expect(health.device).toBe("cuda");
  });
});

describe("Integration: info endpoint", () => {
  let hostA: MockGpuHost;

  beforeAll(async () => {
    hostA = await createMockGpuHost({
      port: PORT_A,
      deviceName: "NVIDIA RTX 2080 Ti",
      vramTotal: 11264,
      vramUsed: 3200,
    });
  });

  afterAll(async () => {
    await hostA.close();
  });

  test("returns GPU info over real HTTP", async () => {
    const client = new GpuBridgeClient({
      hosts: [{ url: hostA.url }],
      healthCheckIntervalSeconds: 600,
    });

    await new Promise((r) => setTimeout(r, 200));

    const info = await client.info();

    expect(info.device).toBe("cuda");
    expect(info.device_name).toBe("NVIDIA RTX 2080 Ti");
    expect(info.vram_total_mb).toBe(11264);
    expect(info.vram_used_mb).toBe(3200);
    expect(info.pytorch_version).toBe("2.5.0");
    expect(info.loaded_models).toContain("all-MiniLM-L6-v2");
  });
});
