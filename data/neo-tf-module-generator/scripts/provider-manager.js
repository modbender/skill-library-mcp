#!/usr/bin/env node
/**
 * Provider Configuration Manager
 *
 * Usage: node provider-manager.js [--provider <provider>] [--validate] [--list]
 *
 * Functions:
 *   - loadProviderConfig(provider): returns config object for the provider
 *   - validateCredentials(provider): async, tests connectivity with cloud providers
 *
 * This module uses config.js for loading configuration and performs
 * active connectivity checks using cloud provider SDKs.
 */

const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Import config.js (must be in the same directory)
const config = require('./config.js');

// Import cloud SDKs
const { EC2Client, DescribeRegionsCommand } = require('@aws-sdk/client-ec2');
const { DefaultAzureCredential } = require('@azure/identity');
const { ResourceManagementClient } = require('@azure/arm-resources');
const { Compute } = require('@google-cloud/compute');

/**
 * Load provider configuration (from env, files, defaults)
 * @param {string} provider - 'aws', 'azure', or 'gcp'
 * @returns {object} Configuration object
 */
async function loadProviderConfig(provider) {
  return config.getConfig(provider);
}

/**
 * Validate credentials by performing a simple API call
 * @param {string} provider - 'aws', 'azure', or 'gcp'
 * @returns {Promise<{valid: boolean, errors: string[], warnings: string[]}>}
 */
async function validateCredentials(provider) {
  const cfg = config.getConfig(provider);
  const errors = [];
  const warnings = [];

  switch (provider) {
    case 'aws':
      try {
        const client = new EC2Client({
          region: cfg.region || 'us-east-1',
          // Credentials are automatically resolved from environment/chain
        });
        // Perform a simple, low-cost call to verify connectivity
        await client.send(new DescribeRegionsCommand({}));
      } catch (err) {
        errors.push(`AWS connection failed: ${err.message}`);
      }
      break;

    case 'azure':
      try {
        if (!cfg.subscription_id) {
          errors.push('Azure subscription_id is required');
          break;
        }
        const credential = new DefaultAzureCredential();
        const resourceClient = new ResourceManagementClient(credential, cfg.subscription_id);
        // Test by fetching a provider list (limit to first page)
        const iterator = resourceClient.providers.list();
        let count = 0;
        for await (const p of iterator) {
          count++;
          if (count >= 1) break; // Only need to confirm access
        }
      } catch (err) {
        errors.push(`Azure connection failed: ${err.message}`);
      }
      break;

    case 'gcp':
      try {
        if (!cfg.project) {
          errors.push('GCP project is required');
          break;
        }
        const compute = new Compute();
        // Listing zones is a quick, project-scoped operation
        await compute.getZones();
      } catch (err) {
        errors.push(`GCP connection failed: ${err.message}`);
      }
      break;

    default:
      errors.push(`Unsupported provider: ${provider}`);
  }

  return { valid: errors.length === 0, errors, warnings };
}

/**
 * List available cloud providers
 * @returns {string[]}
 */
function listProviders() {
  return ['aws', 'azure', 'gcp'];
}

/**
 * Helper to check if a provider has basic credentials configured
 * @private
 */
function providerHasCreds(provider, cfg) {
  switch (provider) {
    case 'aws':
      return !!cfg.access_key || !!cfg.profile || !!cfg.role_arn;
    case 'azure':
      return !!cfg.subscription_id && (!!cfg.client_id || !!cfg.client_secret || cfg.use_cli);
    case 'gcp':
      return !!cfg.project || !!cfg.credentials_file;
    default:
      return false;
  }
}

/**
 * CLI entry point
 */
async function mainCLI() {
  const argv = yargs(hideBin(process.argv))
    .option('provider', {
      alias: 'p',
      type: 'string',
      choices: ['aws', 'azure', 'gcp', 'all'],
      description: 'Cloud provider to manage'
    })
    .option('validate', {
      alias: 'v',
      type: 'boolean',
      description: 'Validate credentials (connects to cloud provider)'
    })
    .option('list', {
      alias: 'l',
      type: 'boolean',
      description: 'List providers with configuration status'
    })
    .argv;

  const provider = argv.provider || 'all';

  // --list: show status for providers
  if (argv.list) {
    const providers = listProviders();
    const status = {};
    for (const p of providers) {
      const cfg = config.getConfig(p);
      status[p] = {
        configured: providerHasCreds(p, cfg),
        region: cfg.region || null,
        project: cfg.project || null,
        subscription: cfg.subscription_id || null
      };
    }
    console.log(JSON.stringify(status, null, 2));
    process.exit(0);
  }

  // --validate: test connectivity
  if (argv.validate) {
    if (provider === 'all') {
      console.error('Specify a provider for validation or use --list to see all.');
      process.exit(1);
    }
    const result = await validateCredentials(provider);
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.valid ? 0 : 1);
  }

  // Default: print configuration for requested provider(s)
  const output = {};
  if (provider === 'all') {
    for (const p of listProviders()) {
      output[p] = config.getConfig(p);
    }
  } else {
    output[provider] = config.getConfig(provider);
  }
  console.log(JSON.stringify(output, null, 2));
}

if (require.main === module) {
  mainCLI().catch(err => {
    console.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
}

module.exports = { loadProviderConfig, validateCredentials, listProviders };
