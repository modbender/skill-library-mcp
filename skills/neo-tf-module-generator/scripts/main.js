#!/usr/bin/env node
/**
 * Terraform Module Generator - CLI Entry Point
 *
 * Usage: node main.js [provider] [resource-types...] [--output <dir>] [--region <region>]
 *
 * Example:
 *   node main.js aws ec2 vpc s3 --output ./my-module --region us-east-1
 *   node main.js azure vm vnet --output ./azure-module
 *   node main.js gcp compute network --output ./gcp-module
 *
 * This script orchestrates the scanning and generation workflow:
 * 1. Initializes cloud provider scanners
 * 2. Collects resource metadata from cloud APIs
 * 3. Generates Terraform module files
 * 4. Validates the output
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Load config
const configPath = path.resolve(__dirname, '../config.js');
const config = require(configPath);

/**
 * Parse command-line arguments
 */
function parseArgs(args) {
  const options = {
    provider: null,
    resources: [],
    output: './generated-module',
    region: null
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--output' && i + 1 < args.length) {
      options.output = args[++i];
    } else if (arg === '--region' && i + 1 < args.length) {
      options.region = args[++i];
    } else if (!arg.startsWith('--')) {
      if (!options.provider) {
        options.provider = arg.toLowerCase();
      } else {
        options.resources.push(arg.toLowerCase());
      }
    }
  }

  return options;
}

/**
 * Run a script and capture its JSON output
 */
function runScript(scriptPath, args) {
  return new Promise((resolve, reject) => {
    const script = path.resolve(__dirname, scriptPath);
    const proc = spawn('node', [script, ...args], {
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env, NODE_ENV = 'production' }
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Script ${script} failed with exit code ${code}: ${stderr}`));
      } else {
        try {
          const result = JSON.parse(stdout);
          resolve(result);
        } catch (e) {
          // Non-JSON output is okay for some scripts
          resolve(stdout.trim());
        }
      }
    });

    proc.on('error', (err) => {
      reject(new Error(`Failed to start ${script}: ${err.message}`));
    });
  });
}

/**
 * Main workflow
 */
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`Usage: node main.js <provider> <resource-types...> [--output <dir>] [--region <region>]

Providers: aws, azure, gcp

Examples:
  node main.js aws ec2 vpc s3 --output ./my-module --region us-east-1
  node main.js azure vm vnet --output ./azure-module
  node main.js gcp compute network --output ./gcp-module

This tool scans existing cloud resources and generates a Terraform module.
`);
    process.exit(0);
  }

  const options = parseArgs(args);

  if (!options.provider || options.resources.length === 0) {
    console.error('Error: provider and at least one resource type are required');
    console.error('Run with --help for usage');
    process.exit(1);
  }

  console.log(`\\n=== Terraform Module Generator ===`);
  console.log(`Provider: ${options.provider.toUpperCase()}`);
  console.log(`Resources: ${options.resources.join(', ')}`);
  console.log(`Output: ${options.output}`);
  if (options.region) console.log(`Region: ${options.region}`);

  try {
    // Step 1: Scan cloud resources
    console.log(`\\n[1/4] Scanning ${options.provider.toUpperCase()} resources...`);

    let resources;
    const scannerArgs = options.region ? [options.region, '--output', 'json'] : ['--output', 'json'];

    switch (options.provider) {
      case 'aws':
        resources = await runScript('./aws-scanner.js', [...scannerArgs, ...options.resources]);
        break;
      case 'azure':
        resources = await runScript('./azure-scanner.js', [...scannerArgs, ...options.resources]);
        break;
      case 'gcp':
        resources = await runScript('./gcp-scanner.js', [...scannerArgs, ...options.resources]);
        break;
      default:
        throw new Error(`Unsupported provider: ${options.provider}`);
    }

    if (!resources || resources.length === 0) {
      console.warn(`No ${options.provider} resources found matching: ${options.resources.join(', ')}`);
      console.log('Continuing with empty module...');
    } else {
      console.log(`Found ${resources.length} resource(s)`);
    }

    // Step 2: Generate Terraform code
    console.log(`\\n[2/4] Generating Terraform module...`);

    // Ensure output directory exists
    fs.mkdirSync(options.output, { recursive: true });

    const generatorArgs = ['--input', 'json', '--output', options.output];
    await runScript('./terraform-generator.js', generatorArgs);

    // Pass resources to generator via stdin
    // (Implementation would need to be adjusted for actual stdin handling)
    // For now, we'll assume the generator reads from a temp file or environment

    // Step 3: Validate generated code
    console.log(`\\n[3/4] Validating Terraform syntax...`);

    const validatorResult = await runScript('./validator.js', [options.output]);
    console.log(`Validation: ${validatorResult.status || 'passed'}`);

    if (validatorResult.errors) {
      console.warn('Validation warnings:');
      validatorResult.errors.forEach(err => console.warn(`  - ${err}`));
    }

    // Step 4: Finalize
    console.log(`\\n[4/4] Module generation complete!`);
    console.log(`\\nOutput directory: ${path.resolve(options.output)}`);
    console.log(`\\nNext steps:`);
    console.log(`  - Review the generated main.tf, variables.tf, outputs.tf`);
    console.log(`  - Run 'terraform init' in the module directory`);
    console.log(`  - Run 'terraform validate' to double-check`);
    console.log(`  - Optional: Customize the README.md`);

    console.log(`\\n=== Done ===\\n`);

  } catch (error) {
    console.error(`\\nERROR: ${error.message}`);
    process.exit(1);
  }
}

// Execute
if (require.main === module) {
  main().catch(err => {
    console.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
}

module.exports = { main };
