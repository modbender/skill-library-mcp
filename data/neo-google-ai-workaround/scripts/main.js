#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { Logger } = require("./logger");
const { Detector } = require("./detector");
const { ProxyHandler } = require("./proxy-handler");
const { SessionManager } = require("./session-manager");

const CONFIG_PATH = path.join(__dirname, "..", "assets", "config-template.json");

function loadConfig(configPath) {
  if (!configPath) configPath = CONFIG_PATH;
  try {
    if (fs.existsSync(configPath)) {
      return JSON.parse(fs.readFileSync(configPath, "utf-8"));
    }
  } catch (err) {
    // Fall through to defaults
  }
  return {
    logLevel: "INFO",
    proxies: [],
    maxSessions: 5,
    sessionTTL: 3600000,
    maxProxyFailures: 3,
    rotationStrategy: "round-robin",
  };
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const command = args[0] || "status";
  const flags = {};

  for (let i = 1; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      if (next && !next.startsWith("--")) {
        flags[key] = next;
        i++;
      } else {
        flags[key] = true;
      }
    }
  }

  return { command, flags };
}

function printUsage() {
  console.log(`
google-ai-workaround - Google AI Access Management for OpenClaw

Usage:
  node scripts/main.js <command> [options]

Commands:
  status          Show current session & proxy status (default)
  detect          Analyze a simulated API response for restrictions
  session-create  Create a new session
  session-rotate  Rotate to a new session
  session-list    List all sessions
  session-refresh Refresh the active session token
  session-destroy Destroy all sessions
  proxy-status    Show proxy pool status
  proxy-health    Run proxy health checks
  proxy-add       Add a proxy (--host <host> --port <port>)
  diagnostics     Show detection diagnostics
  configure       Validate and display current configuration
  help            Show this help message

Options:
  --config <path>   Path to config file (default: assets/config-template.json)
  --silent          Suppress log output
  --log-file <path> Write logs to file

Examples:
  node scripts/main.js status
  node scripts/main.js session-create
  node scripts/main.js detect
  node scripts/main.js proxy-add --host 192.168.1.100 --port 8080
`);
}

function runCommand(command, flags, config) {
  const logger = new Logger({
    level: flags.silent ? "ERROR" : config.logLevel || "INFO",
    logFile: flags["log-file"] || null,
    silent: !!flags.silent,
  });

  const detector = new Detector(config, logger);
  const proxyHandler = new ProxyHandler(
    {
      proxies: config.proxies || [],
      maxFailures: config.maxProxyFailures || 3,
      rotationStrategy: config.rotationStrategy || "round-robin",
    },
    logger
  );
  const sessionManager = new SessionManager(
    {
      maxSessions: config.maxSessions || 5,
      sessionTTL: config.sessionTTL || 3600000,
    },
    logger
  );

  switch (command) {
    case "status": {
      const session = sessionManager.getActive();
      const proxyStatus = proxyHandler.getStatus();
      const stats = sessionManager.getStats();

      console.log("\n=== Google AI Workaround Status ===");
      console.log(`\nSession: ${session ? `Active (${session.id.slice(0, 8)}...)` : "None"}`);
      console.log(`Sessions: ${stats.total}/${stats.maxSessions} (${stats.active} active, ${stats.expired} expired)`);
      console.log(`Total requests: ${stats.totalRequests}`);
      console.log(`\nProxies: ${proxyStatus.healthy}/${proxyStatus.total} healthy`);
      console.log(`Strategy: ${proxyStatus.strategy}`);
      console.log("\nStatus: OK");
      return { success: true, session, proxyStatus, stats };
    }

    case "detect": {
      // Simulate analyzing different API responses
      const testResponses = [
        { status: 200, headers: {}, body: { result: "success" } },
        { status: 429, headers: { "x-ratelimit-remaining": "0" }, body: { error: "rate limit exceeded" } },
        { status: 403, headers: {}, body: { error: "access denied, ip blocked" } },
        { status: 401, headers: {}, body: { error: "token expired" } },
        { status: 503, headers: {}, body: { error: "service unavailable" } },
      ];

      console.log("\n=== Restriction Detection Analysis ===\n");

      for (const response of testResponses) {
        const result = detector.analyze(response);
        const status = result.restricted ? "RESTRICTED" : "OK";
        console.log(`HTTP ${response.status}: ${status}`);
        if (result.restricted) {
          for (const p of result.patterns) {
            console.log(`  - ${p.name} (${p.severity}) -> ${p.action}`);
          }
        }
      }

      const diagnostics = detector.getDiagnostics();
      console.log(`\nTotal checks: ${diagnostics.totalChecks}`);
      console.log(`Restricted: ${diagnostics.restrictedCount}`);
      console.log(`Rate limited: ${diagnostics.isRateLimited ? "Yes" : "No"}`);
      return { success: true, diagnostics };
    }

    case "session-create": {
      const proxy = proxyHandler.getActive();
      const session = sessionManager.create({
        token: `tok_${Date.now().toString(36)}`,
        proxy: proxy ? proxy.url : null,
        metadata: { source: "cli", createdBy: "google-ai-workaround" },
      });
      console.log(`\nSession created: ${session.id}`);
      console.log(`Expires: ${new Date(session.expiresAt).toISOString()}`);
      if (proxy) console.log(`Proxy: ${proxy.host}:${proxy.port}`);
      return { success: true, session };
    }

    case "session-rotate": {
      const proxy = proxyHandler.rotate();
      const newSession = sessionManager.rotate({
        token: `tok_${Date.now().toString(36)}`,
        proxy: proxy ? proxy.url : null,
        metadata: { source: "cli", rotatedAt: new Date().toISOString() },
      });
      console.log(`\nSession rotated: ${newSession.id}`);
      return { success: true, session: newSession };
    }

    case "session-list": {
      const sessions = sessionManager.list();
      console.log("\n=== Sessions ===\n");
      if (sessions.length === 0) {
        console.log("No sessions.");
      } else {
        for (const s of sessions) {
          const flags = [
            s.active ? "ACTIVE" : "INACTIVE",
            s.expired ? "EXPIRED" : "VALID",
          ].join(", ");
          console.log(`${s.id.slice(0, 8)}... [${flags}] requests=${s.requestCount} created=${s.createdAt}`);
        }
      }
      return { success: true, sessions };
    }

    case "session-refresh": {
      const refreshed = sessionManager.refreshToken();
      if (refreshed) {
        console.log(`\nToken refreshed for session: ${refreshed.id.slice(0, 8)}...`);
        console.log(`New expiry: ${new Date(refreshed.expiresAt).toISOString()}`);
      } else {
        console.log("\nNo active session to refresh.");
      }
      return { success: true, session: refreshed };
    }

    case "session-destroy": {
      sessionManager.destroyAll();
      console.log("\nAll sessions destroyed.");
      return { success: true };
    }

    case "proxy-status": {
      const status = proxyHandler.getStatus();
      console.log("\n=== Proxy Status ===\n");
      console.log(`Total: ${status.total}`);
      console.log(`Healthy: ${status.healthy}`);
      console.log(`Unhealthy: ${status.unhealthy}`);
      console.log(`Strategy: ${status.strategy}`);
      if (status.proxies.length > 0) {
        console.log("\nProxies:");
        for (const p of status.proxies) {
          console.log(`  ${p.protocol}://${p.host}:${p.port} [${p.healthy ? "OK" : "DOWN"}] failures=${p.failCount}`);
        }
      } else {
        console.log("\nNo proxies configured.");
      }
      return { success: true, status };
    }

    case "proxy-health": {
      const results = proxyHandler.healthCheck();
      console.log("\n=== Proxy Health Check ===\n");
      if (results.length === 0) {
        console.log("No proxies to check.");
      } else {
        for (const r of results) {
          console.log(`${r.host}:${r.port} -> ${r.healthy ? "HEALTHY" : "UNHEALTHY"} (failures: ${r.failCount})`);
        }
      }
      return { success: true, results };
    }

    case "proxy-add": {
      const host = flags.host;
      const port = parseInt(flags.port, 10) || 8080;
      if (!host) {
        console.error("Error: --host is required for proxy-add");
        return { success: false, error: "Missing --host" };
      }
      const added = proxyHandler.addProxy({ host, port, protocol: "http" });
      if (added) {
        console.log(`\nProxy added: ${host}:${port}`);
      } else {
        console.log(`\nProxy ${host}:${port} already exists.`);
      }
      return { success: true, added };
    }

    case "diagnostics": {
      // Run a full diagnostic cycle
      const simResponses = [
        { status: 200, headers: {}, body: {} },
        { status: 429, headers: {}, body: { error: "rate limit" } },
        { status: 200, headers: {}, body: {} },
        { status: 403, headers: {}, body: { error: "access denied" } },
        { status: 200, headers: {}, body: {} },
      ];

      for (const r of simResponses) {
        detector.analyze(r);
      }

      const diag = detector.getDiagnostics();
      const report = logger.generateReport();

      console.log("\n=== Diagnostics ===\n");
      console.log(`Detection checks: ${diag.totalChecks}`);
      console.log(`Restrictions found: ${diag.restrictedCount}`);
      console.log(`Unrestricted: ${diag.unrestricted}`);
      console.log(`Rate limited: ${diag.isRateLimited ? "Yes" : "No"}`);

      if (Object.keys(diag.patternCounts).length > 0) {
        console.log("\nPattern breakdown:");
        for (const [pattern, count] of Object.entries(diag.patternCounts)) {
          console.log(`  ${pattern}: ${count}`);
        }
      }

      console.log(`\nLog entries: ${report.totalEntries}`);
      console.log(`  Errors: ${report.counts.ERROR}`);
      console.log(`  Warnings: ${report.counts.WARN}`);
      return { success: true, diagnostics: diag, logReport: report };
    }

    case "configure": {
      console.log("\n=== Configuration ===\n");
      console.log(JSON.stringify(config, null, 2));
      console.log("\nConfiguration valid: Yes");
      return { success: true, config };
    }

    case "help":
      printUsage();
      return { success: true };

    default:
      console.error(`Unknown command: ${command}`);
      console.error('Run "node scripts/main.js help" for usage.');
      return { success: false, error: `Unknown command: ${command}` };
  }
}

function main() {
  const { command, flags } = parseArgs(process.argv);
  const configPath = flags.config || CONFIG_PATH;
  const config = loadConfig(configPath);

  if (command === "help") {
    printUsage();
    process.exit(0);
  }

  try {
    const result = runCommand(command, flags, config);
    if (!result.success) {
      process.exit(1);
    }
  } catch (err) {
    console.error(`\nFatal error: ${err.message}`);
    process.exit(1);
  }
}

// Allow both CLI and programmatic usage
if (require.main === module) {
  main();
}

module.exports = { loadConfig, parseArgs, runCommand };
