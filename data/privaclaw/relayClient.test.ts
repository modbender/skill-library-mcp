import { describe, it, expect, vi, beforeEach } from "vitest";
import type { OpenClawRuntime } from "./capabilities";
import { RelayClient } from "./relayClient";

// Mock WebSocket
class MockWebSocket {
  static OPEN = 1;
  readyState = MockWebSocket.OPEN;
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: ((e: unknown) => void) | null = null;
  sent: string[] = [];

  send(data: string) { this.sent.push(data); }
  close() { this.readyState = 3; }

  // Test helpers
  simulateOpen() { this.onopen?.(); }
  simulateMessage(msg: Record<string, unknown>) {
    this.onmessage?.({ data: JSON.stringify(msg) });
  }
}

let mockWs: MockWebSocket;

vi.stubGlobal("WebSocket", class extends MockWebSocket {
  constructor() {
    super();
    mockWs = this;
  }
});

function createMockRuntime(): OpenClawRuntime {
  return {
    executePrompt: vi.fn(async (_prompt, onToken) => {
      onToken("Hello");
      onToken(" world");
    }),
    executeWorkflow: vi.fn(async () => {}),
    getRunningTaskCount: vi.fn(() => 2),
    getLastError: vi.fn(() => null),
    restart: vi.fn(async () => {}),
  };
}

describe("RelayClient message dispatch", () => {
  let client: RelayClient;
  let runtime: ReturnType<typeof createMockRuntime>;

  beforeEach(() => {
    vi.useFakeTimers();
    runtime = createMockRuntime();
    client = new RelayClient(
      { relay_url: "wss://relay.test", node_id: "node-1", auth_token: "tok" },
      runtime
    );
  });

  function connectAndAuth() {
    client.connect();
    mockWs.simulateOpen();
    // Verify hello sent
    const hello = JSON.parse(mockWs.sent[0]);
    expect(hello.type).toBe("hello");
    // Simulate auth ok
    mockWs.simulateMessage({ type: "hello_ok" });
  }

  it("sends hello on connect", () => {
    client.connect();
    mockWs.simulateOpen();
    const msg = JSON.parse(mockWs.sent[0]);
    expect(msg.type).toBe("hello");
    expect(msg.data.node_id).toBe("node-1");
    expect(msg.data.token).toBe("tok");
    client.disconnect();
  });

  it("dispatches prompt to runtime and streams tokens", async () => {
    connectAndAuth();
    mockWs.sent = [];

    mockWs.simulateMessage({
      type: "prompt",
      data: { request_id: "r1", data: { prompt: "Hi" } },
    });

    // Flush microtasks for async dispatch
    await vi.advanceTimersByTimeAsync(0);

    expect(runtime.executePrompt).toHaveBeenCalledWith("Hi", expect.any(Function));

    const responses = mockWs.sent.map(s => JSON.parse(s));
    const tokens = responses.filter(r => r.data?.type === "token");
    const done = responses.find(r => r.data?.type === "done");
    expect(tokens.length).toBe(2);
    expect(tokens[0].data.content).toBe("Hello");
    expect(done?.data.request_id).toBe("r1");

    client.disconnect();
  });

  it("dispatches status request", async () => {
    connectAndAuth();
    mockWs.sent = [];

    mockWs.simulateMessage({
      type: "status",
      data: { request_id: "r2" },
    });

    await vi.advanceTimersByTimeAsync(0);

    const responses = mockWs.sent.map(s => JSON.parse(s));
    const statusResp = responses.find(r => r.data?.type === "status");
    expect(statusResp).toBeDefined();
    expect(statusResp?.data.node_id).toBe("node-1");
    expect(statusResp?.data.active_tasks).toBe(2);

    client.disconnect();
  });

  it("dispatches restart", async () => {
    connectAndAuth();
    mockWs.sent = [];

    mockWs.simulateMessage({
      type: "restart",
      data: { request_id: "r3" },
    });

    await vi.advanceTimersByTimeAsync(0);

    expect(runtime.restart).toHaveBeenCalled();
    client.disconnect();
  });

  it("dispatches workflow", async () => {
    connectAndAuth();
    mockWs.sent = [];

    mockWs.simulateMessage({
      type: "workflow",
      data: { request_id: "r4", data: { workflow_id: "wf-1", params: { x: 1 } } },
    });

    await vi.advanceTimersByTimeAsync(0);

    expect(runtime.executeWorkflow).toHaveBeenCalledWith("wf-1", { x: 1 });
    client.disconnect();
  });

  it("rejects unknown message types silently", async () => {
    connectAndAuth();
    mockWs.sent = [];

    mockWs.simulateMessage({ type: "unknown_garbage", data: {} });
    await vi.advanceTimersByTimeAsync(0);

    expect(mockWs.sent.length).toBe(0);
    client.disconnect();
  });

  it("sends heartbeat after auth", () => {
    connectAndAuth();
    mockWs.sent = [];

    vi.advanceTimersByTime(15_000);

    const heartbeats = mockWs.sent.map(s => JSON.parse(s)).filter(m => m.type === "heartbeat");
    expect(heartbeats.length).toBe(1);
    expect(heartbeats[0].data.node_id).toBe("node-1");

    client.disconnect();
  });
});
