import test from "node:test";
import assert from "node:assert/strict";
import { runPreflightChecks } from "../../src/node/preflight-checks.mjs";

test("preflight passes safe payload", () => {
  assert.doesNotThrow(() =>
    runPreflightChecks({
      slides: ["one", "two", "three", "four", "five", "six"],
      caption: "safe caption",
    })
  );
});

test("preflight fails banned content", () => {
  assert.throws(
    () =>
      runPreflightChecks({
        slides: ["one", "buy now", "three", "four", "five", "six"],
        caption: "safe caption",
      }),
    /Preflight check failed/
  );
});
