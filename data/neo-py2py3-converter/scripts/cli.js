#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");
const { convert, generateReport } = require("./converter");
const { generateTests } = require("./test-generator");

/**
 * Parse command-line arguments into a structured object.
 */
function parseArgs(argv) {
  const args = {
    command: null,
    input: null,
    output: null,
    generateTests: false,
    help: false,
  };

  const raw = argv.slice(2);

  for (let i = 0; i < raw.length; i++) {
    const arg = raw[i];

    if (arg === "--help" || arg === "-h") {
      args.help = true;
    } else if (arg === "--input" || arg === "-i") {
      args.input = raw[++i];
    } else if (arg === "--output" || arg === "-o") {
      args.output = raw[++i];
    } else if (arg === "--generate-tests" || arg === "-t") {
      args.generateTests = true;
    } else if (!arg.startsWith("-") && !args.command) {
      args.command = arg;
    }
  }

  return args;
}

/**
 * Print usage information.
 */
function printHelp() {
  console.log(`
py2py3-converter - Convert Python 2 code to Python 3

Usage:
  node cli.js <command> [options]

Commands:
  convert    Convert Python 2 code to Python 3
  check      Check compatibility without converting

Options:
  --input, -i <file>      Input Python 2 file
  --output, -o <file>     Output Python 3 file (default: stdout)
  --generate-tests, -t    Generate pytest tests for converted code
  --help, -h              Show this help message

Examples:
  node cli.js convert --input file.py --output converted.py
  node cli.js convert --input file.py --generate-tests
  node cli.js check --input file.py
  cat file.py | node cli.js convert
`);
}

/**
 * Read input from file or stdin.
 */
function readInput(inputPath) {
  if (inputPath) {
    if (!fs.existsSync(inputPath)) {
      console.error(`Error: Input file not found: ${inputPath}`);
      process.exit(2);
    }
    return fs.readFileSync(inputPath, "utf-8");
  }

  // Read from stdin if not a TTY
  if (!process.stdin.isTTY) {
    return fs.readFileSync("/dev/stdin", "utf-8");
  }

  console.error("Error: No input provided. Use --input <file> or pipe to stdin.");
  process.exit(2);
}

/**
 * Write output to file or stdout.
 */
function writeOutput(content, outputPath) {
  if (outputPath) {
    const dir = path.dirname(outputPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(outputPath, content, "utf-8");
    console.error(`Written to: ${outputPath}`);
  } else {
    process.stdout.write(content);
  }
}

/**
 * Main entry point.
 */
function main() {
  const args = parseArgs(process.argv);

  if (args.help || !args.command) {
    printHelp();
    process.exit(args.help ? 0 : 1);
  }

  const code = readInput(args.input);

  if (args.command === "check") {
    // Check mode: report only, no conversion output
    const result = convert(code);
    const report = generateReport(result.issues);
    console.log(report);

    const hasErrors = result.issues.some((i) => i.type === "error");
    process.exit(hasErrors ? 2 : 0);
  }

  if (args.command === "convert") {
    const result = convert(code);
    const report = generateReport(result.issues);

    // Write converted code
    writeOutput(result.convertedCode, args.output);

    // Print report to stderr so it doesn't mix with code on stdout
    console.error("\n" + report);

    // Generate tests if requested
    if (args.generateTests) {
      const testCode = generateTests(code, result.convertedCode);
      const testOutputPath = args.output
        ? args.output.replace(/\.py$/, "_test.py")
        : null;

      if (testOutputPath) {
        fs.writeFileSync(testOutputPath, testCode, "utf-8");
        console.error(`Tests written to: ${testOutputPath}`);
      } else {
        console.error("\n=== Generated Tests ===\n");
        console.error(testCode);
      }
    }

    // Exit with appropriate code
    const hasErrors = result.issues.some((i) => i.type === "error");
    const hasWarnings = result.issues.some((i) => i.type === "warning");
    if (hasErrors) {
      process.exit(2);
    } else if (hasWarnings) {
      process.exit(1);
    } else {
      process.exit(0);
    }
  }

  console.error(`Unknown command: ${args.command}`);
  printHelp();
  process.exit(2);
}

main();
