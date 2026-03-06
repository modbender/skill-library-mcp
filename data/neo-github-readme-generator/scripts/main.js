#!/usr/bin/env node

/**
 * GitHub README Generator — CLI entry point.
 *
 * Usage:
 *   node scripts/main.js <repo-url> [--output <file>] [--template <type>] [--no-validate]
 *   node scripts/main.js --help
 *
 * Environment:
 *   GITHUB_TOKEN — optional GitHub personal access token
 */

const fs = require("fs");
const path = require("path");
const { gatherRepoData } = require("./github-api");
const { analyzeRepo } = require("./analyzer");
const { generateReadme } = require("./readme-generator");
const { validate } = require("./validator");

function printUsage() {
  console.log(`
GitHub README Generator

Usage:
  node scripts/main.js <repo-url> [options]

Arguments:
  repo-url              GitHub repository URL (e.g. https://github.com/owner/repo)
                        or shorthand (owner/repo)

Options:
  --output, -o <file>   Write output to file instead of stdout
  --template, -t <type> Force a project type template (nodejs, python, go, rust)
  --no-validate         Skip validation of generated README
  --help, -h            Show this help message

Environment:
  GITHUB_TOKEN          GitHub personal access token (optional for public repos)

Examples:
  node scripts/main.js https://github.com/expressjs/express
  node scripts/main.js octokit/octokit.js --output README.md
  node scripts/main.js owner/repo --template nodejs
`.trim());
}

function parseArgs(argv) {
  const args = {
    repoUrl: null,
    output: null,
    template: null,
    validate: true,
    help: false,
  };

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];

    if (arg === "--help" || arg === "-h") {
      args.help = true;
    } else if (arg === "--output" || arg === "-o") {
      i++;
      args.output = argv[i];
    } else if (arg === "--template" || arg === "-t") {
      i++;
      args.template = argv[i];
    } else if (arg === "--no-validate") {
      args.validate = false;
    } else if (!arg.startsWith("-")) {
      args.repoUrl = arg;
    } else {
      console.error(`Unknown option: ${arg}`);
      process.exit(1);
    }

    i++;
  }

  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printUsage();
    process.exit(0);
  }

  if (!args.repoUrl) {
    console.error("Error: repository URL is required.\n");
    printUsage();
    process.exit(1);
  }

  try {
    // Step 1: Gather repository data from GitHub API
    console.error(`[1/4] Fetching repository data from ${args.repoUrl}...`);
    const repoData = await gatherRepoData(args.repoUrl);

    // Step 2: Analyze repository structure
    console.error(`[2/4] Analyzing repository structure...`);
    const analysis = analyzeRepo(repoData);

    // Override project type if template specified
    if (args.template) {
      analysis.projectType = args.template;
    }

    // Step 3: Generate README
    console.error(`[3/4] Generating README...`);
    const readme = generateReadme(analysis);

    // Step 4: Validate
    if (args.validate) {
      console.error(`[4/4] Validating generated README...`);
      const result = validate(readme);

      if (result.errors.length > 0) {
        console.error(`\nValidation errors:`);
        for (const err of result.errors) {
          console.error(`  - ${err}`);
        }
      }

      if (result.warnings.length > 0) {
        console.error(`\nValidation warnings:`);
        for (const warn of result.warnings) {
          console.error(`  - ${warn}`);
        }
      }

      console.error(`\nQuality score: ${result.score}/100`);
    } else {
      console.error(`[4/4] Skipping validation.`);
    }

    // Output
    if (args.output) {
      const outputPath = path.resolve(args.output);
      fs.writeFileSync(outputPath, readme, "utf-8");
      console.error(`\nREADME written to ${outputPath}`);
    } else {
      process.stdout.write(readme);
    }

    console.error("\nDone.");
    process.exit(0);
  } catch (err) {
    console.error(`\nError: ${err.message}`);
    if (err.status === 404) {
      console.error("Repository not found. Check the URL and ensure it is public or that GITHUB_TOKEN is set.");
    } else if (err.status === 403) {
      console.error("Rate limit exceeded or access denied. Set GITHUB_TOKEN for higher limits.");
    }
    process.exit(1);
  }
}

main();
