#!/usr/bin/env node
import process from "node:process";

function getArg(flag) {
  const i = process.argv.indexOf(flag);
  if (i === -1) return undefined;
  return process.argv[i + 1];
}

function redact(s) {
  if (!s) return s;
  if (s.length <= 6) return "***";
  return `${s.slice(0, 2)}…${s.slice(-2)}`;
}

const tokenId = getArg("--tokenId") || process.env.SOLAX_TOKENID;
const sn = getArg("--sn") || process.env.SOLAX_SN;

if (!tokenId || !sn) {
  console.log(
    JSON.stringify(
      {
        ok: false,
        error: "missing_input",
        missing: {
          tokenId: !tokenId,
          sn: !sn,
        },
        hint: "Provide --tokenId/--sn or set SOLAX_TOKENID and SOLAX_SN",
      },
      null,
      2
    )
  );
  process.exit(2);
}

import { createRequire } from "node:module";

let SolaxCloudAPI, INVERTER_BRAND;
try {
  // solax-cloud-api@0.2.0 ships a broken ESM entry in some builds on Node 22+.
  // Use CJS require to load the working dist/cjs bundle.
  const require = createRequire(import.meta.url);
  const mod = require("solax-cloud-api");

  SolaxCloudAPI = mod.SolaxCloudAPI || mod.default?.SolaxCloudAPI || mod.default;
  INVERTER_BRAND = mod.INVERTER_BRAND || mod.default?.INVERTER_BRAND;

  if (!SolaxCloudAPI) throw new Error("Missing SolaxCloudAPI export");
} catch (e) {
  console.log(
    JSON.stringify(
      {
        ok: false,
        error: "missing_dependency",
        detail:
          "Failed to load solax-cloud-api. Ensure it is installed (npm install in scripts/) and that the package exports are compatible.",
        message: e?.message || String(e),
      },
      null,
      2
    )
  );
  process.exit(3);
}

try {
  const brand = INVERTER_BRAND?.SOLAX ?? 0;
  const api = new SolaxCloudAPI(brand, tokenId, sn);

  const resp = await api.getAPIData();
  if (!resp || resp.success !== true) {
    throw new Error(resp?.exception || "Solax API returned success=false");
  }

  const summary = SolaxCloudAPI.toSummary(resp.result);
  console.log(JSON.stringify(summary, null, 2));
} catch (e) {
  console.log(
    JSON.stringify(
      {
        ok: false,
        error: "solax_api_error",
        message: e?.message || String(e),
        tokenId: redact(tokenId),
        sn,
      },
      null,
      2
    )
  );
  process.exit(1);
}
