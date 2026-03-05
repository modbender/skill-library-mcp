#!/usr/bin/env bun

import process from "node:process";
import { runPipeline } from "../src/pipeline/run";

type ProviderId = "openai" | "gemini" | "claude" | "ollama";

function printUsage(): never {
  console.log(`sec-daily-digest

Usage:
  bun scripts/sec-digest.ts [options]

Options:
  --provider <openai|gemini|claude|ollama>  Provider (default: openai)
  --opml <tiny|full>                         OPML profile (default: tiny)
  --hours <n>                                Time range in hours (default: 48)
  --top-n <n>                                Number of selected items (default: 20)
  --output <path>                            Output markdown path
  --dry-run                                  Use rule-based scoring only
  --help                                     Show help
`);
  process.exit(0);
}

function parseArgs(argv: string[]): {
  provider?: ProviderId;
  opmlProfile?: "tiny" | "full";
  hours?: number;
  topN?: number;
  outputPath?: string;
  dryRun?: boolean;
} {
  const options: {
    provider?: ProviderId;
    opmlProfile?: "tiny" | "full";
    hours?: number;
    topN?: number;
    outputPath?: string;
    dryRun?: boolean;
  } = {};

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]!;
    if (arg === "--provider" && argv[i + 1]) {
      options.provider = argv[i + 1] as ProviderId;
      i += 1;
    } else if (arg === "--opml" && argv[i + 1]) {
      const val = argv[i + 1]!;
      if (val === "tiny" || val === "full") {
        options.opmlProfile = val;
      }
      i += 1;
    } else if (arg === "--hours" && argv[i + 1]) {
      options.hours = Number.parseInt(argv[i + 1]!, 10);
      i += 1;
    } else if (arg === "--top-n" && argv[i + 1]) {
      options.topN = Number.parseInt(argv[i + 1]!, 10);
      i += 1;
    } else if (arg === "--output" && argv[i + 1]) {
      options.outputPath = argv[i + 1]!;
      i += 1;
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--help" || arg === "-h") {
      printUsage();
    }
  }

  return options;
}

const options = parseArgs(process.argv.slice(2));
const startedAt = Date.now();

runPipeline(options)
  .then((result) => {
    const elapsed = ((Date.now() - startedAt) / 1000).toFixed(2);
    console.log(`[sec-digest] provider=${result.provider}`);
    console.log(`[sec-digest] cache_fallback=${result.usedCache}`);
    console.log(`[sec-digest] output=${result.outputPath}`);
    console.log(
      `[sec-digest] stats feeds=${result.counters.feeds} articles=${result.counters.articles} recent=${result.counters.recent} selected=${result.counters.selected} vuln_events=${result.counters.vulnerabilities}`,
    );
    console.log(`[sec-digest] done in ${elapsed}s`);
  })
  .catch((error) => {
    console.error(`[sec-digest] fatal: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  });
