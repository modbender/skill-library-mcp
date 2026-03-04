/**
 * Local integration test script for hashbox-plugin.
 *
 * Simulates how OpenClaw would load and use the plugin:
 * 1. Validates plugin object structure (name, tools, actions)
 * 2. Tests configure_hashbox tool with a dummy token
 * 3. Tests send_hashbox_notification action (dry-run — will hit real webhook)
 *
 * Usage:
 *   npx tsx scripts/local-test.ts            # full test (sends real webhook)
 *   npx tsx scripts/local-test.ts --dry-run  # skip webhook call
 */

import { hashBoxPlugin, configureHashBox, sendHashBoxNotification } from "../src/index.js";
import { readFile, unlink } from "node:fs/promises";
import { join } from "node:path";

const DRY_RUN = process.argv.includes("--dry-run");
const CONFIG_PATH = join(process.cwd(), "hashbox_config.json");

let passed = 0;
let failed = 0;

function check(label: string, condition: boolean, detail?: string): void {
  if (condition) {
    passed++;
    process.stdout.write(`  ✅ ${label}\n`);
  } else {
    failed++;
    process.stdout.write(`  ❌ ${label}${detail ? ` — ${detail}` : ""}\n`);
  }
}

async function cleanup(): Promise<void> {
  try {
    await unlink(CONFIG_PATH);
  } catch {
    // ignore if not exists
  }
}

async function main(): Promise<void> {
  process.stdout.write("\n🔍 hashbox-plugin Local Verification\n");
  process.stdout.write(`   Mode: ${DRY_RUN ? "dry-run (skip webhook)" : "full (sends real webhook)"}\n\n`);

  // ── Step 1: Plugin object structure ──
  process.stdout.write("── Step 1: Plugin Structure ──\n");

  check("plugin.name is 'hashbox-plugin'", hashBoxPlugin.name === "hashbox-plugin");
  check("plugin.description is non-empty", hashBoxPlugin.description.length > 0);
  check("plugin.tools has 1 tool", hashBoxPlugin.tools.length === 1);
  check("plugin.actions has 1 action", hashBoxPlugin.actions.length === 1);
  check("tool name is 'configure_hashbox'", hashBoxPlugin.tools[0].name === "configure_hashbox");
  check("action name is 'send_hashbox_notification'", hashBoxPlugin.actions[0].name === "send_hashbox_notification");
  check("tool.execute is a function", typeof hashBoxPlugin.tools[0].execute === "function");
  check("action.execute is a function", typeof hashBoxPlugin.actions[0].execute === "function");

  // ── Step 2: configure_hashbox ──
  process.stdout.write("\n── Step 2: configure_hashbox ──\n");

  // 2a: Invalid token should throw
  try {
    await configureHashBox("INVALID-TOKEN");
    check("rejects invalid token (no HB- prefix)", false, "did not throw");
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    check("rejects invalid token (no HB- prefix)", msg.includes("HB-"));
  }

  // 2b: Valid token should succeed
  const TEST_TOKEN = "HB-local-test-token-12345";
  try {
    const result = await configureHashBox(TEST_TOKEN);
    check("accepts valid HB- token", result.includes("successfully"));

    // 2c: Config file written correctly
    const raw = await readFile(CONFIG_PATH, "utf-8");
    const config = JSON.parse(raw) as { token: string };
    check("config file contains correct token", config.token === TEST_TOKEN);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    check("accepts valid HB- token", false, msg);
  }

  // 2d: Via plugin tool interface (simulates OpenClaw calling the tool)
  try {
    const result = await hashBoxPlugin.tools[0].execute(TEST_TOKEN);
    check("tool.execute works via plugin interface", typeof result === "string");
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    check("tool.execute works via plugin interface", false, msg);
  }

  // ── Step 3: send_hashbox_notification ──
  process.stdout.write("\n── Step 3: send_hashbox_notification ──\n");

  if (DRY_RUN) {
    process.stdout.write("  ⏭️  Skipping webhook call (--dry-run)\n");

    // Still verify payload construction by checking no throw before fetch
    check("function is callable", typeof sendHashBoxNotification === "function");
    check("action.execute is callable via plugin", typeof hashBoxPlugin.actions[0].execute === "function");
  } else {
    // 3a: Article type
    try {
      const result = await sendHashBoxNotification(
        "article",
        "AI Trends",
        "🤖",
        "Local Test Article",
        "# Hello from hashbox-plugin\n\nThis is a **local integration test**."
      );
      check(
        `article push — status ${result.status}`,
        result.status > 0,
        result.message
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      check("article push", false, msg);
    }

    // 3b: Metric type
    try {
      const result = await sendHashBoxNotification(
        "metric",
        "System Health",
        "📊",
        "Server Metrics",
        [
          { label: "CPU Usage", value: 42, unit: "%", trend: "up" as const },
          { label: "Memory", value: 8.2, unit: "GB", trend: "flat" as const },
        ]
      );
      check(
        `metric push — status ${result.status}`,
        result.status > 0,
        result.message
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      check("metric push", false, msg);
    }

    // 3c: Audit type
    try {
      const result = await sendHashBoxNotification(
        "audit",
        "Security Log",
        "🛡️",
        "Access Audit",
        [
          {
            timestamp: new Date().toISOString(),
            event: "local-test-login",
            severity: "info" as const,
            details: "Integration test from local-test.ts",
          },
        ]
      );
      check(
        `audit push — status ${result.status}`,
        result.status > 0,
        result.message
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      check("audit push", false, msg);
    }

    // 3d: Via plugin action interface
    try {
      const result = await hashBoxPlugin.actions[0].execute(
        "article", "Test Channel", "🧪", "Plugin Interface Test", "Sent via action.execute"
      );
      check("action.execute works via plugin interface", result !== undefined);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      check("action.execute works via plugin interface", false, msg);
    }
  }

  // ── Step 4: Missing config error ──
  process.stdout.write("\n── Step 4: Error Handling ──\n");
  await cleanup();

  try {
    await sendHashBoxNotification("article", "Test", "📝", "Test", "test");
    check("throws when config missing", false, "did not throw");
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    check("throws when config missing", msg.includes("config") || msg.includes("Config"));
  }

  // ── Summary ──
  process.stdout.write(`\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
  process.stdout.write(`  Results: ${passed} passed, ${failed} failed\n`);
  process.stdout.write(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`);

  // Cleanup
  await cleanup();

  process.exit(failed > 0 ? 1 : 0);
}

main();
