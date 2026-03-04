#!/usr/bin/env node
"use strict";

const assert = require("assert");
const path = require("path");
const { Logger, LOG_LEVELS } = require("../scripts/logger");
const { Detector, RESTRICTION_PATTERNS } = require("../scripts/detector");
const { ProxyHandler } = require("../scripts/proxy-handler");
const { SessionManager } = require("../scripts/session-manager");
const { loadConfig, parseArgs, runCommand } = require("../scripts/main");

let passed = 0;
let failed = 0;
const failures = [];

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  \u2713 ${name}`);
  } catch (err) {
    failed++;
    failures.push({ name, error: err.message });
    console.log(`  \u2717 ${name}`);
    console.log(`    ${err.message}`);
  }
}

// ============================================================
// Logger Tests
// ============================================================
console.log("\n=== Logger Tests ===\n");

test("Logger: creates with default options", () => {
  const logger = new Logger({ silent: true });
  assert.strictEqual(logger.level, LOG_LEVELS.INFO);
  assert.strictEqual(logger.entries.length, 0);
});

test("Logger: logs at correct levels", () => {
  const logger = new Logger({ silent: true, level: "DEBUG" });
  logger.debug("debug msg");
  logger.info("info msg");
  logger.warn("warn msg");
  logger.error("error msg");
  assert.strictEqual(logger.entries.length, 4);
  assert.strictEqual(logger.entries[0].level, "DEBUG");
  assert.strictEqual(logger.entries[3].level, "ERROR");
});

test("Logger: filters messages below level", () => {
  const logger = new Logger({ silent: true, level: "WARN" });
  logger.debug("should not appear");
  logger.info("should not appear");
  logger.warn("should appear");
  logger.error("should appear");
  assert.strictEqual(logger.entries.length, 2);
});

test("Logger: categorizes errors correctly", () => {
  const logger = new Logger({ silent: true });

  const network = logger.categorize(new Error("ECONNREFUSED"));
  assert.strictEqual(network.category, "NETWORK");

  const auth = logger.categorize(new Error("401 unauthorized"));
  assert.strictEqual(auth.category, "AUTH");

  const rate = logger.categorize(new Error("429 rate limit"));
  assert.strictEqual(rate.category, "RATE_LIMIT");

  const timeout = logger.categorize(new Error("ETIMEDOUT"));
  assert.strictEqual(timeout.category, "TIMEOUT");

  const proxy = logger.categorize(new Error("proxy error"));
  assert.strictEqual(proxy.category, "PROXY");

  const general = logger.categorize(new Error("something else"));
  assert.strictEqual(general.category, "GENERAL");
});

test("Logger: generates report", () => {
  const logger = new Logger({ silent: true, level: "DEBUG" });
  logger.info("test1");
  logger.error("test2");
  logger.warn("test3");
  const report = logger.generateReport();
  assert.strictEqual(report.totalEntries, 3);
  assert.strictEqual(report.counts.INFO, 1);
  assert.strictEqual(report.counts.ERROR, 1);
  assert.strictEqual(report.counts.WARN, 1);
});

test("Logger: getEntries filters by level", () => {
  const logger = new Logger({ silent: true, level: "DEBUG" });
  logger.info("a");
  logger.error("b");
  logger.info("c");
  assert.strictEqual(logger.getEntries("INFO").length, 2);
  assert.strictEqual(logger.getEntries("ERROR").length, 1);
});

test("Logger: clear removes all entries", () => {
  const logger = new Logger({ silent: true });
  logger.info("a");
  logger.info("b");
  logger.clear();
  assert.strictEqual(logger.entries.length, 0);
});

// ============================================================
// Detector Tests
// ============================================================
console.log("\n=== Detector Tests ===\n");

test("Detector: detects rate limiting (429)", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze({ status: 429, headers: {}, body: {} });
  assert.strictEqual(result.restricted, true);
  assert.ok(result.patterns.some((p) => p.id === "rate_limit"));
});

test("Detector: detects auth expired (401)", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze({ status: 401, headers: {}, body: {} });
  assert.strictEqual(result.restricted, true);
  assert.ok(result.patterns.some((p) => p.id === "auth_expired"));
});

test("Detector: detects IP block (403 with ip keyword)", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze({
    status: 403,
    headers: {},
    body: { error: "ip blocked" },
  });
  assert.strictEqual(result.restricted, true);
  assert.ok(result.patterns.some((p) => p.id === "ip_block"));
});

test("Detector: detects geo block (403 with region keyword)", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze({
    status: 403,
    headers: {},
    body: { error: "region restricted" },
  });
  assert.strictEqual(result.restricted, true);
  assert.ok(result.patterns.some((p) => p.id === "geo_block"));
});

test("Detector: detects service unavailable (503)", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze({ status: 503, headers: {}, body: {} });
  assert.strictEqual(result.restricted, true);
  assert.ok(result.patterns.some((p) => p.id === "service_unavailable"));
});

test("Detector: returns OK for 200 response", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze({
    status: 200,
    headers: {},
    body: { result: "ok" },
  });
  assert.strictEqual(result.restricted, false);
  assert.strictEqual(result.patterns.length, 0);
});

test("Detector: isAccessible works correctly", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  assert.strictEqual(detector.isAccessible({ status: 200 }), true);
  assert.strictEqual(detector.isAccessible({ status: 201 }), true);
  assert.strictEqual(detector.isAccessible({ status: 403 }), false);
  assert.strictEqual(detector.isAccessible({ status: 500 }), false);
  assert.strictEqual(detector.isAccessible(null), false);
});

test("Detector: getRecommendedAction returns highest severity action", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze({
    status: 403,
    headers: {},
    body: { error: "ip blocked and access denied" },
  });
  const action = detector.getRecommendedAction(result);
  assert.strictEqual(action, "switch_proxy"); // IP block is critical
});

test("Detector: handles invalid response gracefully", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  const result = detector.analyze(null);
  assert.strictEqual(result.restricted, false);
  const result2 = detector.analyze({});
  assert.strictEqual(result2.restricted, false);
});

test("Detector: getDiagnostics returns correct counts", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  detector.analyze({ status: 200, headers: {}, body: {} });
  detector.analyze({ status: 429, headers: {}, body: {} });
  detector.analyze({ status: 200, headers: {}, body: {} });

  const diag = detector.getDiagnostics();
  assert.strictEqual(diag.totalChecks, 3);
  assert.strictEqual(diag.restrictedCount, 1);
  assert.strictEqual(diag.unrestricted, 2);
});

test("Detector: isRateLimited detects sustained rate limiting", () => {
  const detector = new Detector({}, new Logger({ silent: true }));
  for (let i = 0; i < 5; i++) {
    detector.analyze({ status: 429, headers: {}, body: {} });
  }
  assert.strictEqual(detector.isRateLimited(5), true);
});

// ============================================================
// ProxyHandler Tests
// ============================================================
console.log("\n=== ProxyHandler Tests ===\n");

test("ProxyHandler: initializes with config proxies", () => {
  const handler = new ProxyHandler(
    { proxies: [{ host: "p1.test", port: 8080 }] },
    new Logger({ silent: true })
  );
  const status = handler.getStatus();
  assert.strictEqual(status.total, 1);
  assert.strictEqual(status.healthy, 1);
});

test("ProxyHandler: getActive returns proxy with round-robin", () => {
  const handler = new ProxyHandler(
    {
      proxies: [
        { host: "p1.test", port: 8080 },
        { host: "p2.test", port: 8080 },
      ],
    },
    new Logger({ silent: true })
  );
  const first = handler.getActive();
  assert.strictEqual(first.host, "p1.test");
  const second = handler.getActive();
  assert.strictEqual(second.host, "p2.test");
  const third = handler.getActive();
  assert.strictEqual(third.host, "p1.test");
});

test("ProxyHandler: returns null when no proxies configured", () => {
  const handler = new ProxyHandler({}, new Logger({ silent: true }));
  assert.strictEqual(handler.getActive(), null);
});

test("ProxyHandler: markFailed tracks failures", () => {
  const handler = new ProxyHandler(
    {
      proxies: [{ host: "p1.test", port: 8080 }],
      maxFailures: 2,
    },
    new Logger({ silent: true })
  );
  handler.markFailed("p1.test");
  const status1 = handler.getStatus();
  assert.strictEqual(status1.healthy, 1);

  handler.markFailed("p1.test");
  const status2 = handler.getStatus();
  assert.strictEqual(status2.healthy, 0);
});

test("ProxyHandler: markHealthy resets failure count", () => {
  const handler = new ProxyHandler(
    {
      proxies: [{ host: "p1.test", port: 8080 }],
      maxFailures: 2,
    },
    new Logger({ silent: true })
  );
  handler.markFailed("p1.test");
  handler.markHealthy("p1.test");
  const status = handler.getStatus();
  assert.strictEqual(status.healthy, 1);
  assert.strictEqual(status.proxies[0].failCount, 0);
});

test("ProxyHandler: addProxy adds a new proxy", () => {
  const handler = new ProxyHandler({}, new Logger({ silent: true }));
  const result = handler.addProxy({ host: "new.test", port: 3128 });
  assert.strictEqual(result, true);
  assert.strictEqual(handler.getStatus().total, 1);
});

test("ProxyHandler: addProxy rejects duplicates", () => {
  const handler = new ProxyHandler(
    { proxies: [{ host: "p1.test", port: 8080 }] },
    new Logger({ silent: true })
  );
  const result = handler.addProxy({ host: "p1.test", port: 8080 });
  assert.strictEqual(result, false);
});

test("ProxyHandler: removeProxy removes a proxy", () => {
  const handler = new ProxyHandler(
    { proxies: [{ host: "p1.test", port: 8080 }] },
    new Logger({ silent: true })
  );
  const result = handler.removeProxy("p1.test");
  assert.strictEqual(result, true);
  assert.strictEqual(handler.getStatus().total, 0);
});

test("ProxyHandler: healthCheck runs on all proxies", () => {
  const handler = new ProxyHandler(
    {
      proxies: [
        { host: "p1.test", port: 8080 },
        { host: "p2.test", port: 8080 },
      ],
    },
    new Logger({ silent: true })
  );
  const results = handler.healthCheck();
  assert.strictEqual(results.length, 2);
});

test("ProxyHandler: parses string proxy URLs", () => {
  const handler = new ProxyHandler(
    { proxies: ["http://user:pass@proxy.test:9090"] },
    new Logger({ silent: true })
  );
  const active = handler.getActive();
  assert.strictEqual(active.host, "proxy.test");
  assert.strictEqual(active.port, 9090);
});

// ============================================================
// SessionManager Tests
// ============================================================
console.log("\n=== SessionManager Tests ===\n");

test("SessionManager: creates a session", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  const session = sm.create({ token: "test-token" });
  assert.ok(session.id);
  assert.strictEqual(session.token, "test-token");
  assert.strictEqual(session.active, true);
  sm.destroyAll();
});

test("SessionManager: getActive returns current session", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  const created = sm.create({ token: "tok" });
  const active = sm.getActive();
  assert.strictEqual(active.id, created.id);
  sm.destroyAll();
});

test("SessionManager: getActive returns null when no session", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  assert.strictEqual(sm.getActive(), null);
});

test("SessionManager: rotate creates new session and deactivates old", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  const old = sm.create({ token: "old" });
  const newSession = sm.rotate({ token: "new" });
  assert.notStrictEqual(old.id, newSession.id);
  const active = sm.getActive();
  assert.strictEqual(active.id, newSession.id);
  sm.destroyAll();
});

test("SessionManager: refreshToken updates token", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  sm.create({ token: "original" });
  const refreshed = sm.refreshToken();
  assert.ok(refreshed.token.startsWith("tok_"));
  assert.notStrictEqual(refreshed.token, "original");
  sm.destroyAll();
});

test("SessionManager: destroy removes session", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  const session = sm.create({});
  assert.strictEqual(sm.destroy(session.id), true);
  assert.strictEqual(sm.getActive(), null);
});

test("SessionManager: destroyAll clears all sessions", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  sm.create({});
  sm.create({});
  sm.destroyAll();
  assert.strictEqual(sm.list().length, 0);
});

test("SessionManager: evicts oldest when at capacity", () => {
  const sm = new SessionManager(
    {
      maxSessions: 2,
      sessionDir: path.join(__dirname, ".sessions-test"),
    },
    new Logger({ silent: true })
  );
  sm.create({ metadata: { n: 1 } });
  sm.create({ metadata: { n: 2 } });
  sm.create({ metadata: { n: 3 } });
  assert.strictEqual(sm.list().length, 2);
  sm.destroyAll();
});

test("SessionManager: list returns session summaries", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  sm.create({});
  const list = sm.list();
  assert.strictEqual(list.length, 1);
  assert.ok("id" in list[0]);
  assert.ok("active" in list[0]);
  sm.destroyAll();
});

test("SessionManager: getStats returns correct statistics", () => {
  const sm = new SessionManager(
    { sessionDir: path.join(__dirname, ".sessions-test") },
    new Logger({ silent: true })
  );
  sm.create({});
  sm.recordActivity();
  sm.recordActivity();
  const stats = sm.getStats();
  assert.strictEqual(stats.total, 1);
  assert.strictEqual(stats.active, 1);
  assert.strictEqual(stats.totalRequests, 2);
  sm.destroyAll();
});

// ============================================================
// Main module Tests
// ============================================================
console.log("\n=== Main Module Tests ===\n");

test("parseArgs: parses command and flags", () => {
  const result = parseArgs(["node", "main.js", "detect", "--silent", "--config", "test.json"]);
  assert.strictEqual(result.command, "detect");
  assert.strictEqual(result.flags.silent, true);
  assert.strictEqual(result.flags.config, "test.json");
});

test("parseArgs: defaults to status command", () => {
  const result = parseArgs(["node", "main.js"]);
  assert.strictEqual(result.command, "status");
});

test("loadConfig: loads config from file", () => {
  const config = loadConfig(path.join(__dirname, "..", "assets", "config-template.json"));
  assert.ok(config.logLevel);
  assert.ok(Array.isArray(config.proxies));
});

test("loadConfig: returns defaults for missing file", () => {
  const config = loadConfig("/nonexistent/path.json");
  assert.ok(config.logLevel);
  assert.ok(Array.isArray(config.proxies));
});

test("runCommand: status returns success", () => {
  const config = { logLevel: "ERROR", proxies: [], maxSessions: 5 };
  const result = runCommand("status", { silent: true }, config);
  assert.strictEqual(result.success, true);
});

test("runCommand: detect returns success with diagnostics", () => {
  const config = { logLevel: "ERROR", proxies: [] };
  const result = runCommand("detect", { silent: true }, config);
  assert.strictEqual(result.success, true);
  assert.ok(result.diagnostics);
});

test("runCommand: session-create returns session", () => {
  const config = { logLevel: "ERROR", proxies: [] };
  const result = runCommand("session-create", { silent: true }, config);
  assert.strictEqual(result.success, true);
  assert.ok(result.session.id);
});

test("runCommand: configure returns config", () => {
  const config = { logLevel: "INFO", proxies: [] };
  const result = runCommand("configure", { silent: true }, config);
  assert.strictEqual(result.success, true);
});

test("runCommand: unknown command returns failure", () => {
  const config = { logLevel: "ERROR", proxies: [] };
  const result = runCommand("nonexistent", { silent: true }, config);
  assert.strictEqual(result.success, false);
});

test("runCommand: diagnostics returns success", () => {
  const config = { logLevel: "ERROR", proxies: [] };
  const result = runCommand("diagnostics", { silent: true }, config);
  assert.strictEqual(result.success, true);
  assert.ok(result.diagnostics);
  assert.ok(result.logReport);
});

test("runCommand: proxy-status returns success", () => {
  const config = { logLevel: "ERROR", proxies: [{ host: "test.proxy", port: 8080 }] };
  const result = runCommand("proxy-status", { silent: true }, config);
  assert.strictEqual(result.success, true);
});

test("runCommand: proxy-add requires host", () => {
  const config = { logLevel: "ERROR", proxies: [] };
  const result = runCommand("proxy-add", { silent: true }, config);
  assert.strictEqual(result.success, false);
});

test("runCommand: proxy-add with host succeeds", () => {
  const config = { logLevel: "ERROR", proxies: [] };
  const result = runCommand("proxy-add", { silent: true, host: "new.proxy", port: "9090" }, config);
  assert.strictEqual(result.success, true);
});

test("runCommand: help returns success", () => {
  const config = { logLevel: "ERROR", proxies: [] };
  const result = runCommand("help", { silent: true }, config);
  assert.strictEqual(result.success, true);
});

// ============================================================
// Summary
// ============================================================
console.log("\n=== Test Summary ===\n");
console.log(`Total: ${passed + failed}`);
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);

if (failures.length > 0) {
  console.log("\nFailures:");
  for (const f of failures) {
    console.log(`  - ${f.name}: ${f.error}`);
  }
}

console.log("");
process.exit(failed > 0 ? 1 : 0);
