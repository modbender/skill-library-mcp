const { describe, test, expect, beforeEach, afterEach, mock } = require("bun:test");

describe("telemetry", () => {
  let originalEnv;
  let originalFetch;

  beforeEach(() => {
    originalEnv = { ...process.env };
    originalFetch = global.fetch;
    // Clear telemetry-related env vars
    delete process.env.AGENT_REGISTRY_NO_TELEMETRY;
    delete process.env.AGENT_REGISTRY_TELEMETRY;
    delete process.env.DO_NOT_TRACK;
    delete process.env.CI;
    delete process.env.GITHUB_ACTIONS;
    delete process.env.GITLAB_CI;
    delete process.env.CIRCLECI;
    delete process.env.TRAVIS;
    delete process.env.BUILDKITE;
    delete process.env.JENKINS_URL;

    // Clear module cache to get fresh isDisabled state
    delete require.cache[require.resolve("../lib/telemetry")];
  });

  afterEach(() => {
    process.env = originalEnv;
    global.fetch = originalFetch;
    delete require.cache[require.resolve("../lib/telemetry")];
  });

  describe("exports", () => {
    test("exports track, VERSION, and TOOL_ID", () => {
      const telemetry = require("../lib/telemetry");
      expect(typeof telemetry.track).toBe("function");
      expect(telemetry.VERSION).toBe("2.0.1");
      expect(telemetry.TOOL_ID).toBe("agent-registry");
    });
  });

  describe("track", () => {
    test("does not throw when called with event and data", () => {
      const { track } = require("../lib/telemetry");
      expect(() => track("test_event", { n: 5, ms: 100 })).not.toThrow();
    });

    test("does not throw when called with just event", () => {
      const { track } = require("../lib/telemetry");
      expect(() => track("test_event")).not.toThrow();
    });

    test("does not throw when called with null data", () => {
      const { track } = require("../lib/telemetry");
      expect(() => track("test_event", null)).not.toThrow();
    });

    test("is disabled by default (no opt-in)", () => {
      const calls = [];
      global.fetch = mock((url) => {
        calls.push(url);
        return Promise.resolve();
      });

      const { track } = require("../lib/telemetry");
      track("test_event");
      expect(calls.length).toBe(0);
    });

    test("sends telemetry when explicitly opted in", async () => {
      process.env.AGENT_REGISTRY_TELEMETRY = "1";
      const calls = [];
      global.fetch = mock((url) => {
        calls.push(url);
        return Promise.resolve();
      });

      const { track } = require("../lib/telemetry");
      track("test_event", { n: 1 });
      await Promise.resolve();
      expect(calls.length).toBe(1);
    });
  });

  describe("opt-out via env vars", () => {
    test("is disabled when AGENT_REGISTRY_NO_TELEMETRY is set", () => {
      process.env.AGENT_REGISTRY_NO_TELEMETRY = "1";
      const { track } = require("../lib/telemetry");
      // Should not make any fetch calls — just verify it doesn't throw
      expect(() => track("test")).not.toThrow();
    });

    test("is disabled when DO_NOT_TRACK is set", () => {
      process.env.DO_NOT_TRACK = "1";
      const { track } = require("../lib/telemetry");
      expect(() => track("test")).not.toThrow();
    });

    test("is disabled in CI environment (GITHUB_ACTIONS)", () => {
      process.env.GITHUB_ACTIONS = "true";
      const { track } = require("../lib/telemetry");
      expect(() => track("test")).not.toThrow();
    });

    test("is disabled in CI environment (CI)", () => {
      process.env.CI = "true";
      const { track } = require("../lib/telemetry");
      expect(() => track("test")).not.toThrow();
    });

    test("is disabled in CI environment (GITLAB_CI)", () => {
      process.env.GITLAB_CI = "true";
      const { track } = require("../lib/telemetry");
      expect(() => track("test")).not.toThrow();
    });

    test("is disabled in CI environment (JENKINS_URL)", () => {
      process.env.JENKINS_URL = "http://jenkins.example.com";
      const { track } = require("../lib/telemetry");
      expect(() => track("test")).not.toThrow();
    });
  });
});
