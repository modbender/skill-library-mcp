#!/usr/bin/env node

import chalk from "chalk";

import { VIBE_HUB_URL_DEFAULT, isMainModule } from "./constants.mjs";

// Tag types to fetch
const TAG_TYPES = ["platform", "tech-stack", "model", "category"];

/**
 * Fetch tags from API
 * @param {string} hubUrl - Hub URL
 * @param {string} type - Tag type
 * @returns {Promise<Array>} Tags array
 */
async function fetchTagsByType(hubUrl, type) {
  const { origin } = new URL(hubUrl);
  const url = `${origin}/api/tags?type=${type}&isActive=true`;

  const response = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch ${type} tags: ${response.status} ${response.statusText}`);
  }

  const result = await response.json();
  return result.data || [];
}

/**
 * Fetch all tags from API (parallel)
 * @param {string} hubUrl - Hub URL
 * @returns {Promise<Object>} Tags object by type
 */
async function fetchAllTags(hubUrl) {
  const results = await Promise.allSettled(TAG_TYPES.map((type) => fetchTagsByType(hubUrl, type)));

  const tags = {};
  results.forEach((result, index) => {
    const type = TAG_TYPES[index];
    if (result.status === "fulfilled") {
      tags[type] = result.value;
    } else {
      console.error(chalk.yellow(`Warning: Failed to fetch ${type} tags: ${result.reason.message}`));
      tags[type] = [];
    }
  });

  return tags;
}

/**
 * Get tags from API
 * @param {Object} options - Options
 * @param {string} [options.hub] - Hub URL
 * @param {boolean} [options.silent] - Suppress console output
 * @returns {Promise<Object>} Tags result
 */
export async function getTags(options = {}) {
  const { hub = VIBE_HUB_URL_DEFAULT, silent = false } = options;

  const log = silent ? () => {} : console.error.bind(console);

  log(chalk.cyan(`Fetching tags from ${hub}...`));

  try {
    const tags = await fetchAllTags(hub);

    return {
      success: true,
      hub,
      tags,
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Parse command line arguments
 */
function parseArgs(args) {
  const options = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    const nextArg = args[i + 1];

    switch (arg) {
      case "--hub":
      case "-h":
        options.hub = nextArg;
        i++;
        break;
      case "--help":
        printHelp();
        process.exit(0);
        break;
    }
  }

  return options;
}

/**
 * Print help message
 */
function printHelp() {
  console.log(`
${chalk.bold("MyVibe Tags Fetcher")}

Fetch available tags from MyVibe.

${chalk.bold("Usage:")}
  node fetch-tags.mjs [options]

${chalk.bold("Options:")}
  --hub, -h <url>    MyVibe URL (default: ${VIBE_HUB_URL_DEFAULT})
  --help             Show this help message

${chalk.bold("Output:")}
  JSON object with tags grouped by type (platform, tech-stack, model, category)

${chalk.bold("Examples:")}
  # Fetch tags
  node fetch-tags.mjs

  # Use specific hub
  node fetch-tags.mjs --hub https://myvibe.example.com
`);
}

// CLI entry point
if (isMainModule(import.meta.url)) {
  const args = process.argv.slice(2);
  const options = parseArgs(args);

  getTags({ ...options, silent: false })
    .then((result) => {
      // Output JSON to stdout for AI to parse
      console.log(JSON.stringify(result, null, 2));
      process.exit(result.success ? 0 : 1);
    })
    .catch((error) => {
      console.error(chalk.red(`Fatal error: ${error.message}`));
      process.exit(1);
    });
}

export default getTags;
