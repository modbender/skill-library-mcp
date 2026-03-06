/**
 * Tests for the main openclaw-ops-elvatis entry point (index.ts).
 *
 * Verifies that register() wires up all extension modules and respects
 * the enabled/workspacePath config options.
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { createMockApi } from "./src/test-helpers.js";
import register from "./index.js";

describe("register (entry point)", () => {
  it("registers all expected commands", () => {
    const api = createMockApi();
    register(api);

    // Phase 1 commands
    expect(api.commands.has("health")).toBe(true);
    expect(api.commands.has("services")).toBe(true);
    expect(api.commands.has("logs")).toBe(true);
    expect(api.commands.has("plugins")).toBe(true);

    // Legacy commands
    expect(api.commands.has("cron")).toBe(true);
    expect(api.commands.has("privacy-scan")).toBe(true);
    expect(api.commands.has("release")).toBe(true);
    expect(api.commands.has("staging-smoke")).toBe(true);
    expect(api.commands.has("handoff")).toBe(true);
    expect(api.commands.has("limits")).toBe(true);

    // Observer commands
    expect(api.commands.has("sessions")).toBe(true);
    expect(api.commands.has("activity")).toBe(true);
    expect(api.commands.has("session-tail")).toBe(true);
    expect(api.commands.has("session-stats")).toBe(true);
    expect(api.commands.has("session-clear")).toBe(true);

    // Skills commands
    expect(api.commands.has("skills")).toBe(true);
    expect(api.commands.has("shortcuts")).toBe(true);

    // Config commands
    expect(api.commands.has("config")).toBe(true);
  });

  it("does not register commands when enabled is false", () => {
    const api = createMockApi({ enabled: false });
    register(api);
    expect(api.commands.size).toBe(0);
  });

  it("registers commands when enabled is undefined (default)", () => {
    const api = createMockApi({});
    register(api);
    expect(api.commands.size).toBeGreaterThan(0);
  });

  it("accepts a custom workspacePath", () => {
    const api = createMockApi({ workspacePath: "/tmp/test-workspace" });
    // Should not throw
    register(api);
    expect(api.commands.size).toBeGreaterThan(0);
  });

  it("hooks the message_received event for observer", () => {
    const api = createMockApi();
    register(api);
    expect(api.eventHandlers.has("message_received")).toBe(true);
    expect(api.eventHandlers.get("message_received")!.length).toBeGreaterThan(0);
  });

  it("registers exactly 18 commands total", () => {
    const api = createMockApi();
    register(api);
    // 4 phase1 + 6 legacy + 5 observer + 2 skills + 1 config = 18
    expect(api.commands.size).toBe(18);
  });
});
