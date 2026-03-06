#!/usr/bin/env node

/**
 * Quick market analysis - combines market info + orderbook in one call
 * Usage: quick-analysis.mjs <ticker>
 */

import { spawn } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CLI = join(__dirname, "kalshi-cli.mjs");

function exec(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn("node", [CLI, ...args], { stdio: "pipe" });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (data) => (stdout += data.toString()));
    proc.stderr.on("data", (data) => (stderr += data.toString()));
    proc.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr || "Command failed"));
      } else {
        try {
          resolve(JSON.parse(stdout));
        } catch (e) {
          reject(new Error(`Failed to parse JSON: ${e.message}`));
        }
      }
    });
  });
}

async function main() {
  const ticker = process.argv[2];
  if (!ticker) {
    console.error("Usage: quick-analysis.mjs <ticker>");
    process.exit(1);
  }

  try {
    const [market, orderbook] = await Promise.all([
      exec(["market", ticker]),
      exec(["orderbook", ticker]),
    ]);

    const analysis = {
      ticker: market.ticker,
      title: market.title,
      subtitle: market.subtitle,
      status: market.status,
      pricing: {
        yes_bid: market.yes_bid,
        yes_ask: market.yes_ask,
        no_bid: market.no_bid,
        no_ask: market.no_ask,
        last_price: market.last_price,
        spread: (parseFloat(market.yes_ask) - parseFloat(market.yes_bid)).toFixed(4),
      },
      volume: {
        total: market.volume,
        last_24h: market.volume_24h,
        open_interest: market.open_interest,
      },
      liquidity: market.liquidity,
      orderbook: {
        yes_depth: orderbook.yes.length,
        no_depth: orderbook.no.length,
        yes_levels: orderbook.yes.slice(0, 3),
        no_levels: orderbook.no.slice(0, 3),
      },
      timing: {
        close_time: market.close_time,
      },
      rules: market.rules_primary,
    };

    console.log(JSON.stringify(analysis, null, 2));
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }
}

main();
