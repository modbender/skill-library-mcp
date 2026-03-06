#!/usr/bin/env npx tsx
/**
 * list-offerings.ts
 *
 * Lists all x402janus scan tiers and prices available on the ACP marketplace.
 * Fetches the x402janus agent profile from the ACP API and displays its job offerings.
 *
 * Usage:
 *   npx tsx scripts/list-offerings.ts [--json]
 *
 * Environment:
 *   ACP_API_KEY    — Virtuals ACP API key (required)
 *   ACP_BASE_URL   — ACP base URL (default: https://claw-api.virtuals.io)
 */

import { parseArgs } from "util";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface JobOffering {
  id: number;
  name: string;
  type: string;
  price: number;
  priceV2?: { type: string; value: number };
  slaMinutes: number;
  deliverable: string;
  description: string;
  requirement: Record<string, string>;
  requiredFunds: boolean;
}

interface AgentProfile {
  id: number;
  name: string;
  description: string;
  walletAddress: string;
  profilePic: string | null;
  jobs: JobOffering[];
  enabledChains: Array<{ id: number; name: string }>;
}

// ---------------------------------------------------------------------------
// Fetch
// ---------------------------------------------------------------------------

async function fetchProfile(apiKey: string, baseUrl: string): Promise<AgentProfile> {
  const resp = await fetch(`${baseUrl}/acp/me`, {
    headers: {
      "x-api-key": apiKey,
      "Content-Type": "application/json",
    },
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`ACP API error: ${resp.status} ${resp.statusText} — ${body.slice(0, 200)}`);
  }

  const json = await resp.json() as { data: AgentProfile };
  return json.data;
}

// ---------------------------------------------------------------------------
// Display
// ---------------------------------------------------------------------------

function printOfferings(profile: AgentProfile, json: boolean): void {
  const offerings = profile.jobs;

  if (json) {
    console.log(JSON.stringify({
      agent: {
        id: profile.id,
        name: profile.name,
        description: profile.description,
        wallet: profile.walletAddress,
        chains: profile.enabledChains.map(c => c.name),
      },
      offerings: offerings.map(o => ({
        name: o.name,
        price: o.price,
        currency: "VIRTUAL",
        slaMinutes: o.slaMinutes,
        description: o.description,
        requirement: o.requirement,
      })),
    }, null, 2));
    return;
  }

  console.log(`\n🔲  x402janus ACP Offerings\n`);
  console.log(`Agent: ${profile.name} (ID: ${profile.id})`);
  console.log(`Chains: ${profile.enabledChains.map(c => c.name).join(", ")}`);
  console.log(`Wallet: ${profile.walletAddress}`);
  console.log(`\n${"─".repeat(60)}`);

  if (offerings.length === 0) {
    console.log("  No offerings registered.");
    return;
  }

  for (const o of offerings) {
    const price = o.priceV2 ? `$${o.priceV2.value} (${o.priceV2.type})` : `$${o.price}`;
    console.log(`\n  📦 ${o.name}`);
    console.log(`     Price:       ${price} VIRTUAL`);
    console.log(`     SLA:         ${o.slaMinutes} minutes`);
    console.log(`     Description: ${o.description}`);
    if (o.requirement && Object.keys(o.requirement).length > 0) {
      console.log(`     Requires:    ${JSON.stringify(o.requirement)}`);
    }
  }

  console.log(`\n${"─".repeat(60)}\n`);
  console.log(`  ${offerings.length} offering(s) available.\n`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const { values } = parseArgs({
    args: process.argv.slice(2),
    options: {
      json: { type: "boolean", default: false },
      help: { type: "boolean", short: "h", default: false },
    },
    allowPositionals: false,
  });

  if (values.help) {
    console.log(`
x402janus — list ACP marketplace offerings

Usage: npx tsx scripts/list-offerings.ts [--json]

Options:
  --json       Output as JSON
  --help, -h   Show this help

Environment:
  ACP_API_KEY    Virtuals ACP API key (required)
  ACP_BASE_URL   ACP base URL (default: https://claw-api.virtuals.io)
`);
    process.exit(0);
  }

  const apiKey = process.env.ACP_API_KEY;
  if (!apiKey) {
    console.error("Error: ACP_API_KEY environment variable is not set.");
    console.error("Get your key from the Virtuals ACP dashboard.");
    process.exit(1);
  }

  const baseUrl = (process.env.ACP_BASE_URL ?? "https://claw-api.virtuals.io").replace(/\/$/, "");

  try {
    const profile = await fetchProfile(apiKey, baseUrl);
    printOfferings(profile, values.json ?? false);
  } catch (err) {
    console.error("Error:", err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
