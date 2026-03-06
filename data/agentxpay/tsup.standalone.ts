import { defineConfig } from "tsup";

/**
 * Standalone build config for OpenClaw deployment.
 *
 * Bundles everything (including @agentxpay/sdk) into self-contained files.
 * Only `ethers` remains external (peer dependency, too large to inline).
 *
 * Usage:
 *   npm run build:standalone
 *
 * Produces:
 *   dist/index.js / index.mjs  — library entry (SDK inlined)
 *   dist/run-tool.js           — CLI entry for OpenClaw tool dispatch
 */
export default defineConfig({
  entry: {
    index: "src/index.ts",
    "run-tool": "scripts/run-tool.ts",
  },
  format: ["cjs"],
  dts: false,
  splitting: false,
  sourcemap: true,
  clean: true,
  // Only ethers stays external — @agentxpay/sdk will be inlined
  external: ["ethers"],
  noExternal: ["@agentxpay/sdk"],
  banner: {
    js: "#!/usr/bin/env node",
  },
});
