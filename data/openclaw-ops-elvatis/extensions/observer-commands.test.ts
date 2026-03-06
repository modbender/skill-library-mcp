/**
 * Tests for observer commands (/sessions, /activity, /session-tail, /session-stats, /session-clear).
 *
 * Uses a temp directory for the observer event log and memory files.
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { createMockApi, invokeCommand, type MockApi } from "../src/test-helpers.js";
import { registerObserverCommands } from "./observer-commands.js";

const tmpWorkspace = path.join(os.tmpdir(), "openclaw-ops-elvatis-test-observer-" + process.pid);

describe("observer-commands registration", () => {
  let api: MockApi;

  beforeEach(() => {
    fs.mkdirSync(tmpWorkspace, { recursive: true });
    api = createMockApi();
    registerObserverCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("registers /sessions command", () => {
    expect(api.commands.has("sessions")).toBe(true);
    expect(api.commands.get("sessions")!.acceptsArgs).toBe(true);
  });

  it("registers /activity command", () => {
    expect(api.commands.has("activity")).toBe(true);
    expect(api.commands.get("activity")!.acceptsArgs).toBe(true);
  });

  it("registers /session-tail command", () => {
    expect(api.commands.has("session-tail")).toBe(true);
    expect(api.commands.get("session-tail")!.acceptsArgs).toBe(true);
  });

  it("registers /session-stats command", () => {
    expect(api.commands.has("session-stats")).toBe(true);
    expect(api.commands.get("session-stats")!.acceptsArgs).toBe(false);
  });

  it("registers /session-clear command with auth required", () => {
    const cmd = api.commands.get("session-clear")!;
    expect(cmd).toBeDefined();
    expect(cmd.requireAuth).toBe(true);
  });

  it("registers exactly 5 commands", () => {
    expect(api.commands.size).toBe(5);
  });

  it("hooks the message_received event", () => {
    expect(api.eventHandlers.has("message_received")).toBe(true);
  });
});

describe("/sessions handler (empty state)", () => {
  let api: MockApi;

  beforeEach(() => {
    fs.mkdirSync(tmpWorkspace, { recursive: true });
    api = createMockApi();
    registerObserverCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("returns Sessions heading with 0 total", async () => {
    const text = await invokeCommand(api, "sessions", { args: "" });
    expect(text).toContain("Sessions");
    expect(text).toContain("No sessions observed yet");
  });
});

describe("/sessions handler (with events)", () => {
  let api: MockApi;
  const observerDir = path.join(tmpWorkspace, "observer");

  beforeEach(() => {
    fs.mkdirSync(observerDir, { recursive: true });
    // Write some test events
    const events = [
      { ts: "2026-02-27T10:00:00Z", type: "message", sessionId: "sess-abc-123", from: "user", preview: "Hello" },
      { ts: "2026-02-27T10:01:00Z", type: "message", sessionId: "sess-abc-123", from: "user", preview: "World" },
      { ts: "2026-02-27T10:05:00Z", type: "message", sessionId: "sess-def-456", from: "bot", preview: "Response" },
    ];
    const content = events.map(e => JSON.stringify(e)).join("\n") + "\n";
    fs.writeFileSync(path.join(observerDir, "events.jsonl"), content, "utf-8");

    api = createMockApi();
    registerObserverCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("shows session count", async () => {
    const text = await invokeCommand(api, "sessions", { args: "" });
    expect(text).toContain("2 total");
  });

  it("shows session IDs (truncated format)", async () => {
    const text = await invokeCommand(api, "sessions", { args: "" });
    expect(text).toContain("sess-abc");
  });

  it("shows message counts", async () => {
    const text = await invokeCommand(api, "sessions", { args: "" });
    expect(text).toContain("Messages:");
  });
});

describe("/activity handler", () => {
  let api: MockApi;
  const observerDir = path.join(tmpWorkspace, "observer");

  beforeEach(() => {
    fs.mkdirSync(observerDir, { recursive: true });
    const events = [
      { ts: "2026-02-27T10:00:00Z", type: "message", sessionId: "sess-001", preview: "Hello world" },
      { ts: "2026-02-27T10:01:00Z", type: "tool_call", sessionId: "sess-001", tool: "readFile", preview: "Reading config" },
    ];
    fs.writeFileSync(
      path.join(observerDir, "events.jsonl"),
      events.map(e => JSON.stringify(e)).join("\n") + "\n",
      "utf-8",
    );
    api = createMockApi();
    registerObserverCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("shows Activity heading", async () => {
    const text = await invokeCommand(api, "activity", { args: "" });
    expect(text).toContain("Activity");
  });

  it("shows events with previews", async () => {
    const text = await invokeCommand(api, "activity", { args: "" });
    expect(text).toContain("Hello world");
  });

  it("can filter by session ID", async () => {
    const text = await invokeCommand(api, "activity", { args: "sess-001" });
    expect(text).toContain("sess-001");
  });

  it("handles empty activity gracefully", async () => {
    // Clear the log
    fs.writeFileSync(path.join(observerDir, "events.jsonl"), "", "utf-8");
    const text = await invokeCommand(api, "activity", { args: "" });
    expect(text).toContain("No activity recorded yet");
  });
});

describe("/session-tail handler", () => {
  let api: MockApi;
  const observerDir = path.join(tmpWorkspace, "observer");

  beforeEach(() => {
    fs.mkdirSync(observerDir, { recursive: true });
    const events = Array.from({ length: 5 }, (_, i) => ({
      ts: `2026-02-27T10:0${i}:00Z`,
      type: "message",
      sessionId: "sess-tail",
      preview: `Event ${i}`,
    }));
    fs.writeFileSync(
      path.join(observerDir, "events.jsonl"),
      events.map(e => JSON.stringify(e)).join("\n") + "\n",
      "utf-8",
    );
    api = createMockApi();
    registerObserverCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("shows Session tail heading", async () => {
    const text = await invokeCommand(api, "session-tail", { args: "5" });
    expect(text).toContain("Session tail");
  });

  it("respects limit parameter", async () => {
    const text = await invokeCommand(api, "session-tail", { args: "2" });
    expect(text).toContain("last 2 events");
  });

  it("shows events in tail order (oldest first)", async () => {
    const text = await invokeCommand(api, "session-tail", { args: "5" });
    const idx0 = text.indexOf("Event 0");
    const idx4 = text.indexOf("Event 4");
    expect(idx0).toBeLessThan(idx4);
  });
});

describe("/session-stats handler", () => {
  let api: MockApi;
  const observerDir = path.join(tmpWorkspace, "observer");

  beforeEach(() => {
    fs.mkdirSync(observerDir, { recursive: true });
    api = createMockApi();
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("shows no data message when empty", async () => {
    fs.writeFileSync(path.join(observerDir, "events.jsonl"), "", "utf-8");
    registerObserverCommands(api, tmpWorkspace);
    const text = await invokeCommand(api, "session-stats");
    expect(text).toContain("No data yet");
  });

  it("shows overview with counts when events exist", async () => {
    const events = [
      { ts: "2026-02-27T10:00:00Z", type: "message", sessionId: "s1", preview: "test" },
      { ts: "2026-02-27T10:01:00Z", type: "message", sessionId: "s1", preview: "test2" },
      { ts: "2026-02-27T10:02:00Z", type: "message", sessionId: "s2", preview: "other" },
    ];
    fs.writeFileSync(
      path.join(observerDir, "events.jsonl"),
      events.map(e => JSON.stringify(e)).join("\n") + "\n",
      "utf-8",
    );
    registerObserverCommands(api, tmpWorkspace);
    const text = await invokeCommand(api, "session-stats");
    expect(text).toContain("OVERVIEW");
    expect(text).toContain("Total sessions:");
    expect(text).toContain("Total events:");
  });
});

describe("/session-clear handler", () => {
  let api: MockApi;
  const observerDir = path.join(tmpWorkspace, "observer");

  beforeEach(() => {
    fs.mkdirSync(observerDir, { recursive: true });
    const events = [
      { ts: "2026-02-27T10:00:00Z", type: "message", sessionId: "s1", preview: "test" },
    ];
    fs.writeFileSync(
      path.join(observerDir, "events.jsonl"),
      events.map(e => JSON.stringify(e)).join("\n") + "\n",
      "utf-8",
    );
    api = createMockApi();
    registerObserverCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("clears the event log and reports count", async () => {
    const text = await invokeCommand(api, "session-clear");
    expect(text).toContain("cleared");
    expect(text).toContain("1");
  });

  it("event log is empty after clear", async () => {
    await invokeCommand(api, "session-clear");
    const content = fs.readFileSync(path.join(observerDir, "events.jsonl"), "utf-8");
    expect(content).toBe("");
  });
});

describe("message_received event handler", () => {
  let api: MockApi;
  const observerDir = path.join(tmpWorkspace, "observer");

  beforeEach(() => {
    fs.mkdirSync(tmpWorkspace, { recursive: true });
    api = createMockApi();
    registerObserverCommands(api, tmpWorkspace);
  });

  afterEach(() => {
    try { fs.rmSync(tmpWorkspace, { recursive: true, force: true }); } catch {}
  });

  it("appends event to log when message is received", async () => {
    const handler = api.eventHandlers.get("message_received")![0];
    await handler(
      { content: "Hello from test", from: "test-user" },
      { sessionId: "test-session-id", messageProvider: "cli" },
    );

    const logContent = fs.readFileSync(path.join(observerDir, "events.jsonl"), "utf-8");
    expect(logContent).toContain("Hello from test");
    expect(logContent).toContain("test-session-id");
  });

  it("ignores empty messages", async () => {
    const handler = api.eventHandlers.get("message_received")![0];
    await handler({ content: "" }, { sessionId: "test" });

    const logContent = fs.readFileSync(path.join(observerDir, "events.jsonl"), "utf-8");
    // Should only have events from registration, not the empty message
    const lines = logContent.split("\n").filter(l => l.trim());
    expect(lines.length).toBe(0);
  });
});
