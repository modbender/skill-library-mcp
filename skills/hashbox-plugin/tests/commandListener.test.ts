import { describe, it, expect, vi, beforeEach } from "vitest";

// --- Mock firebase/firestore ---
type SnapshotCallback = (snapshot: unknown) => void;
let capturedCallback: SnapshotCallback;
const mockUnsubscribe = vi.fn();
const mockUpdateDoc = vi.fn().mockResolvedValue(undefined);

vi.mock("firebase/firestore", () => ({
  collection: vi.fn((_db: unknown, name: string) => ({ path: name })),
  query: vi.fn((...args: unknown[]) => ({ args })),
  where: vi.fn((field: string, op: string, value: string) => ({
    type: "where",
    field,
    op,
    value,
  })),
  orderBy: vi.fn((field: string) => ({ type: "orderBy", field })),
  onSnapshot: vi.fn((_query: unknown, callback: SnapshotCallback) => {
    capturedCallback = callback;
    return mockUnsubscribe;
  }),
  doc: vi.fn((_db: unknown, collection: string, id: string) => ({
    path: `${collection}/${id}`,
  })),
  updateDoc: (...args: unknown[]) => mockUpdateDoc(...args),
}));

import { startCommandListener } from "../src/commandListener.js";
import type { AgentCommand } from "../src/types.js";

function makeSnapshot(docs: Array<{ id: string; data: Record<string, unknown> }>) {
  return {
    docChanges: () =>
      docs.map((d) => ({
        type: "added" as const,
        doc: {
          id: d.id,
          data: () => d.data,
        },
      })),
  };
}

describe("startCommandListener", () => {
  const mockDb = { type: "firestore" } as unknown as import("firebase/firestore").Firestore;
  const userId = "test-user-123";

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should return unsubscribe function", () => {
    const handler = vi.fn();
    const unsub = startCommandListener(mockDb, userId, handler);
    expect(typeof unsub).toBe("function");
  });

  it("should set up query with correct filters", async () => {
    const { where, orderBy } = await import("firebase/firestore");
    const handler = vi.fn();
    startCommandListener(mockDb, userId, handler);

    expect(where).toHaveBeenCalledWith("userId", "==", userId);
    expect(where).toHaveBeenCalledWith("status", "==", "pending");
    expect(orderBy).toHaveBeenCalledWith("createdAt");
  });

  it("should process pending command: processing → completed", async () => {
    const handler = vi.fn().mockResolvedValue(undefined);
    startCommandListener(mockDb, userId, handler);

    capturedCallback(
      makeSnapshot([
        {
          id: "cmd-1",
          data: {
            userId,
            commandType: "add_feed",
            payload: { topic: "AI", raw_instruction: "Track AI news" },
            status: "pending",
          },
        },
      ]),
    );

    // Wait for async processing
    await new Promise((resolve) => setTimeout(resolve, 10));

    // Should mark as processing first, then completed
    expect(mockUpdateDoc).toHaveBeenCalledTimes(2);

    const firstCall = mockUpdateDoc.mock.calls[0];
    expect(firstCall[0]).toEqual({ path: "agent_commands/cmd-1" });
    expect(firstCall[1]).toEqual({ status: "processing" });

    const secondCall = mockUpdateDoc.mock.calls[1];
    expect(secondCall[0]).toEqual({ path: "agent_commands/cmd-1" });
    expect(secondCall[1]).toEqual({ status: "completed" });
  });

  it("should pass correct AgentCommand to handler", async () => {
    const handler = vi.fn().mockResolvedValue(undefined);
    startCommandListener(mockDb, userId, handler);

    capturedCallback(
      makeSnapshot([
        {
          id: "cmd-2",
          data: {
            userId,
            commandType: "ping_metrics",
            payload: { raw_instruction: "Run health check" },
            status: "pending",
          },
        },
      ]),
    );

    await new Promise((resolve) => setTimeout(resolve, 10));

    expect(handler).toHaveBeenCalledOnce();
    const command = handler.mock.calls[0][0] as AgentCommand;
    expect(command.id).toBe("cmd-2");
    expect(command.userId).toBe(userId);
    expect(command.commandType).toBe("ping_metrics");
    expect(command.payload.raw_instruction).toBe("Run health check");
  });

  it("should mark as error when handler throws", async () => {
    const handler = vi.fn().mockRejectedValue(new Error("Handler failed"));
    startCommandListener(mockDb, userId, handler);

    capturedCallback(
      makeSnapshot([
        {
          id: "cmd-fail",
          data: {
            userId,
            commandType: "add_feed",
            payload: { topic: "Bad", raw_instruction: "Fail me" },
            status: "pending",
          },
        },
      ]),
    );

    await new Promise((resolve) => setTimeout(resolve, 10));

    expect(mockUpdateDoc).toHaveBeenCalledTimes(2);

    const firstCall = mockUpdateDoc.mock.calls[0];
    expect(firstCall[1]).toEqual({ status: "processing" });

    const secondCall = mockUpdateDoc.mock.calls[1];
    expect(secondCall[1]).toEqual({ status: "error" });
  });

  it("should ignore non-added document changes", async () => {
    const handler = vi.fn();
    startCommandListener(mockDb, userId, handler);

    capturedCallback({
      docChanges: () => [
        {
          type: "modified",
          doc: {
            id: "cmd-modified",
            data: () => ({
              userId,
              commandType: "add_feed",
              payload: { raw_instruction: "Modified" },
              status: "processing",
            }),
          },
        },
      ],
    });

    await new Promise((resolve) => setTimeout(resolve, 10));
    expect(handler).not.toHaveBeenCalled();
  });

  it("should process multiple commands in a single snapshot", async () => {
    const handler = vi.fn().mockResolvedValue(undefined);
    startCommandListener(mockDb, userId, handler);

    capturedCallback(
      makeSnapshot([
        {
          id: "cmd-a",
          data: {
            userId,
            commandType: "add_feed",
            payload: { topic: "A", raw_instruction: "Track A" },
            status: "pending",
          },
        },
        {
          id: "cmd-b",
          data: {
            userId,
            commandType: "ping_metrics",
            payload: { raw_instruction: "Ping" },
            status: "pending",
          },
        },
      ]),
    );

    await new Promise((resolve) => setTimeout(resolve, 50));

    expect(handler).toHaveBeenCalledTimes(2);
    // Each command goes through processing → completed = 4 updateDoc calls
    expect(mockUpdateDoc).toHaveBeenCalledTimes(4);
  });

  it("should call unsubscribe when returned function is invoked", () => {
    const handler = vi.fn();
    const unsub = startCommandListener(mockDb, userId, handler);
    unsub();
    expect(mockUnsubscribe).toHaveBeenCalledOnce();
  });
});
