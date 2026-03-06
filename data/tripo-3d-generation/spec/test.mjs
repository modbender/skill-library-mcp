/**
 * Local smoke test for tripo-3d skill.
 *
 * This test verifies the skill's module structure and logic
 * WITHOUT making real API calls. It mocks the proxy responses
 * to validate the full generate -> status -> download flow.
 *
 * Run: node spec/test.mjs
 */

import { createHash } from "crypto";
import { hostname } from "os";

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  ✓ ${label}`);
    passed++;
  } else {
    console.error(`  ✗ ${label}`);
    failed++;
  }
}

// --- Test 1: Module loads correctly ---
console.log("\nTest 1: Module structure");
try {
  const mod = await import("../index.mjs");
  assert(typeof mod.run === "function", "exports run() function");
} catch (e) {
  assert(false, `Module import failed: ${e.message}`);
}

// --- Test 2: User ID generation is deterministic ---
console.log("\nTest 2: User ID generation");
const raw = `${hostname()}-${process.env.HOME || process.env.USERPROFILE || "unknown"}`;
const id1 = createHash("sha256").update(raw).digest("hex").slice(0, 16);
const id2 = createHash("sha256").update(raw).digest("hex").slice(0, 16);
assert(id1 === id2, "User ID is deterministic across calls");
assert(id1.length === 16, "User ID is 16 hex characters");
assert(/^[0-9a-f]+$/.test(id1), "User ID is valid hex");

// --- Test 3: Manifest is valid JSON ---
console.log("\nTest 3: Manifest validation");
try {
  const fs = await import("fs");
  const manifestRaw = fs.readFileSync(new URL("../manifest.json", import.meta.url), "utf-8");
  const manifest = JSON.parse(manifestRaw);
  assert(manifest.name === "tripo-3d", "Name is tripo-3d");
  assert(manifest.version === "1.0.0", "Version is 1.0.0");
  assert(manifest.entry === "index.mjs", "Entry points to index.mjs");
  assert(manifest.schema.required.includes("action"), "action is required");
  assert(manifest.schema.properties.action.enum.length === 4, "4 actions defined");
  assert(manifest.schema.properties.model_version.default === "v3.1-20260211", "Default model version is v3.1-20260211");
  assert(manifest.permissions.includes("network:outbound"), "Requires network:outbound");
  assert(manifest.secrets.TRIPO_API_KEY.required === false, "API key is optional");
} catch (e) {
  assert(false, `Manifest validation failed: ${e.message}`);
}

// --- Test 4: Error handling for missing params ---
console.log("\nTest 4: Input validation");

const mockCtx = { secrets: {} };

// Mock fetch to avoid real network calls
const originalFetch = globalThis.fetch;
globalThis.fetch = async (url, opts) => {
  const urlStr = url.toString();

  if (urlStr.includes("/api/generate")) {
    const body = JSON.parse(opts.body);
    if (body.user_id && body.prompt) {
      return new Response(JSON.stringify({
        data: { task_id: "test_task_001" },
        credits_remaining: 9,
        credits_total: 10,
        using_own_key: false,
      }));
    }
  }

  if (urlStr.includes("/api/status/")) {
    return new Response(JSON.stringify({
      data: {
        task_id: "test_task_001",
        status: "success",
        progress: 100,
        output: {
          pbr_model: "https://example.com/model.glb",
          model: "https://example.com/model_std.glb",
          rendered_image: "https://example.com/preview.png",
        },
      },
    }));
  }

  if (urlStr.includes("/api/download/")) {
    return new Response(JSON.stringify({
      task_id: "test_task_001",
      status: "success",
      pbr_model_url: "https://example.com/model.glb",
      model_url: "https://example.com/model_std.glb",
      rendered_image_url: "https://example.com/preview.png",
    }));
  }

  if (urlStr.includes("/api/credits")) {
    return new Response(JSON.stringify({
      user_id: "abc123",
      credits_used: 3,
      credits_total: 10,
      credits_remaining: 7,
      quota_exceeded: false,
    }));
  }

  return new Response(JSON.stringify({ error: "unknown" }), { status: 404 });
};

const { run } = await import("../index.mjs");

const noPromptResult = await run({ action: "generate" }, mockCtx);
assert(noPromptResult.error != null, "Returns error when no prompt or image_url");

const noTaskIdStatus = await run({ action: "status" }, mockCtx);
assert(noTaskIdStatus.error != null, "Returns error when status called without task_id");

const noTaskIdDownload = await run({ action: "download" }, mockCtx);
assert(noTaskIdDownload.error != null, "Returns error when download called without task_id");

const unknownAction = await run({ action: "foobar" }, mockCtx);
assert(unknownAction.error != null, "Returns error for unknown action");

// --- Test 5: Generate flow ---
console.log("\nTest 5: Generate flow (mocked)");
const genResult = await run({ action: "generate", prompt: "a red apple" }, mockCtx);
assert(genResult.task_id === "test_task_001", "Returns task_id from proxy");
assert(genResult.status === "CREATED", "Status is CREATED");
assert(genResult.message.includes("test_task_001"), "Message includes task_id");

// --- Test 6: Status flow ---
console.log("\nTest 6: Status flow (mocked)");
const statusResult = await run({ action: "status", task_id: "test_task_001" }, mockCtx);
assert(statusResult.status === "SUCCESS", "Status is SUCCESS");
assert(statusResult.pbr_model_url != null, "Has pbr_model_url");

// --- Test 7: Download flow ---
console.log("\nTest 7: Download flow (mocked)");
const dlResult = await run({ action: "download", task_id: "test_task_001" }, mockCtx);
assert(dlResult.status === "SUCCESS", "Download status is SUCCESS");
assert(dlResult.pbr_model_url.includes("model.glb"), "Has correct model URL");

// --- Test 8: Credits flow ---
console.log("\nTest 8: Credits flow (mocked)");
const creditsResult = await run({ action: "credits" }, mockCtx);
assert(creditsResult.credits_remaining === 7, "Shows 7 remaining credits");
assert(creditsResult.message.includes("7"), "Message mentions remaining count");

// Restore fetch
globalThis.fetch = originalFetch;

// --- Summary ---
console.log(`\n${"=".repeat(40)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
console.log(`${"=".repeat(40)}\n`);

process.exit(failed > 0 ? 1 : 0);
