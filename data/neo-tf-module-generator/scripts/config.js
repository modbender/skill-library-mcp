#!/usr/bin/env node
/**
 * Configuration Manager
 *
 * Usage: node config.js [--provider <provider>] [--get <key>] [--list]
 *
 * Example:
 *   node config.js --list
 *   node config.js --provider aws --get region
 *   node config.js --provider azure
 *
 * Manages cloud provider credentials and settings:
 *   - Loads configuration from environment variables and config files
 *   - Provides unified config object for scanners and generators
 *   - Validates credential presence
 *   - Supports multiple providers
 *
 * Config sources (in order):
 *   1. Environment variables (preferred)
 *   2. ~/.terraform.d/credentials (if present)
 *   3. ./config.json (local project config)
 *   4. Default values
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse arguments
const argv = yargs(hideBin(process.argv))
  .option('provider', {
    alias: 'p',
    type: 'string',
    choices: ['aws', 'azure', 'gcp', 'all'],
    description: 'Cloud provider to configure'
  })
  .option('get', {
    alias: 'g',
    type: 'string',
    description: 'Get a specific config value'
  })
  .option('list', {
    alias: 'l',
    type: 'boolean',
    description: 'List all configuration settings'
  })
  .option('validate', {
    alias: 'v',
    type: 'boolean',
    description: 'Validate credentials and connectivity'
  })
  .argv;

// Configuration defaults
const DEFAULTS = {
  aws: {
    region: 'us-east-1',
    profile: null, // from AWS_PROFILE
    access_key: null, // from AWS_ACCESS_KEY_ID
    secret_key: null, // from AWS_SECRET_ACCESS_KEY
    session_token: null, // from AWS_SESSION_TOKEN
    role_arn: null, // from AWS_ROLE_ARN
    external_id: null // from AWS_EXTERNAL_ID
  },
  azure: {
    subscription_id: null, // from AZURE_SUBSCRIPTION_ID
    tenant_id: null, // from AZURE_TENANT_ID
    client_id: null, // from AZURE_CLIENT_ID (service principal)
    client_secret: null, // from AZURE_CLIENT_SECRET
    location: null, // from AZURE_LOCATION
    use_cli: false // Use 'az login' credentials if true
  },
  gcp: {
    project: null, // from GCP_PROJECT or GOOGLE_CLOUD_PROJECT
    region: null, // from GCP_REGION or GOOGLE_REGION
    zone: null, // from GCP_ZONE or GOOGLE_ZONE
    credentials_file: null, // from GOOGLE_APPLICATION_CREDENTIALS
    use_default: true // Use default credential chain
  }
};

/**
 * Load configuration from environment variables
 */
function loadFromEnv(provider) {
  const config = { ...DEFAULTS[provider] };

  switch (provider) {
    case 'aws':
      config.region = process.env.AWS_REGION || process.env.AWS_DEFAULT_REGION || config.region;
      config.profile = process.env.AWS_PROFILE || null;
      config.access_key = process.env.AWS_ACCESS_KEY_ID || null;
      config.secret_key = process.env.AWS_SECRET_ACCESS_KEY || null;
      config.session_token = process.env.AWS_SESSION_TOKEN || null;
      config.role_arn = process.env.AWS_ROLE_ARN || null;
      break;

    case 'azure':
      config.subscription_id = process.env.AZURE_SUBSCRIPTION_ID || null;
      config.tenant_id = process.env.AZURE_TENANT_ID || null;
      config.client_id = process.env.AZURE_CLIENT_ID || null;
      config.client_secret = process.env.AZURE_CLIENT_SECRET || null;
      config.location = process.env.AZURE_LOCATION || process.env.AZURE_REGION || null;
      config.use_cli = process.env.AZURE_USE_CLI === 'true';
      break;

    case 'gcp':
      config.project = process.env.GCP_PROJECT || process.env.GOOGLE_CLOUD_PROJECT || null;
      config.region = process.env.GCP_REGION || process.env.GOOGLE_REGION || null;
      config.zone = process.env.GCP_ZONE || process.env.GOOGLE_ZONE || null;
      config.credentials_file = process.env.GOOGLE_APPLICATION_CREDENTIALS || null;
      config.use_default = process.env.GOOGLE_USE_DEFAULT !== 'false';
      break;
  }

  return config;
}

/**
 * Load configuration from local file
 */
function loadFromFile(provider) {
  const candidates = [
    path.join(process.cwd(), 'config.json'),
    path.join(process.cwd(), '.terraformrc'),
    path.join(os.homedir(), '.terraform.d', 'credentials'),
    path.join(os.homedir(), '.config', 'terraform', 'credentials')
  ];

  for (const filePath of candidates) {
    if (fs.existsSync(filePath)) {
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const config = JSON.parse(content);

        if (config[provider]) {
          return config[provider];
        }

        // HCL-style credentials file (simplified)
        if (typeof config === 'object' && !config[provider]) {
          // Check if it's a credentials block
          const creds = config.credentials || config;
          if (creds[provider]) {
            return creds[provider];
          }
        }
      } catch (e) {
        // Ignore parse errors, try next file
      }
    }
  }

  return {};
}

/**
 * Validate AWS configuration
 */
function validateAWS(config) {
  const errors = [];
  const warnings = [];

  if (!config.access_key && !config.profile && !config.role_arn) {
    errors.push('AWS credentials not found. Set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY or use AWS_PROFILE or IAM role.');
  }

  if (config.role_arn && !config.access_key && !config.secret_key) {
    warnings.push('Using IAM role with default credential chain (no explicit keys)');
  }

  if (!config.region) {
    warnings.push('AWS region not set, defaulting to us-east-1');
  }

  return { valid: errors.length === 0, errors, warnings };
}

/**
 * Validate Azure configuration
 */
function validateAzure(config) {
  const errors = [];
  const warnings = [];

  if (!config.subscription_id) {
    errors.push('Azure subscription ID not set (AZURE_SUBSCRIPTION_ID)');
  }

  if (!config.client_id && !config.use_cli) {
    errors.push('Azure credentials not configured. Set AZURE_CLIENT_ID or use AZURE_USE_CLI=true with az login');
  }

  if (config.use_cli && !config.location) {
    warnings.push('Using az login; consider setting AZURE_LOCATION');
  }

  return { valid: errors.length === 0, errors, warnings };
}

/**
 * Validate GCP configuration
 */
function validateGCP(config) {
  const errors = [];
  const warnings = [];

  if (!config.project) {
    errors.push('GCP project not set (GCP_PROJECT or GOOGLE_CLOUD_PROJECT)');
  }

  if (!config.credentials_file && !config.use_default) {
    warnings.push('GCP credentials not explicitly set; relying on default credential chain');
  }

  return { valid: errors.length === 0, errors, warnings };
}

/**
 * Get full configuration for a provider
 */
function getConfig(provider) {
  let config = loadFromEnv(provider);
  const fileConfig = loadFromFile(provider);

  // Merge: file config overrides env if present? No, env takes precedence
  // Actually: file config is fallback, env overrides file
  // So we already have env-loaded config; merge file config as defaults only
  const merged = { ...DEFAULTS[provider], ...fileConfig, ...config };
  return merged;
}

/**
 * List all configuration for one or all providers
 */
function listConfig(provider) {
  const providers = provider === 'all' ? ['aws', 'azure', 'gcp'] : [provider];
  const output = {};

  for (const p of providers) {
    output[p] = getConfig(p);
  }

  return output;
}

/**
 * Main entry
 */
async function main() {
  const provider = argv.provider || 'all';

  if (argv.list) {
    const config = listConfig(provider);
    console.log(JSON.stringify(config, null, 2));
    process.exit(0);
  }

  if (argv.get) {
    if (!argv.provider) {
      console.error('Error: --provider is required with --get');
      process.exit(1);
    }
    const config = getConfig(provider);
    console.log(config[argv.get] || '');
    process.exit(0);
  }

  if (argv.validate) {
    console.error(`Validating ${provider.toUpperCase()} configuration...`);

    const config = getConfig(provider);
    let validation;

    switch (provider) {
      case 'aws':
        validation = validateAWS(config);
        break;
      case 'azure':
        validation = validateAzure(config);
        break;
      case 'gcp':
        validation = validateGCP(config);
        break;
      default:
        console.error('Error: must specify a provider for validation');
        process.exit(1);
    }

    if (validation.valid) {
      console.error(`✓ ${provider.toUpperCase()} configuration is valid`);
      if (validation.warnings.length > 0) {
        console.error('Warnings:');
        validation.warnings.forEach(w => console.error(`  - ${w}`));
      }
      process.exit(0);
    } else {
      console.error(`✗ ${provider.toUpperCase()} configuration is invalid:`);
      validation.errors.forEach(e => console.error(`  - ${e}`));
      process.exit(1);
    }
  }

  // Default: print useful info
  const config = getConfig(provider);
  console.log(JSON.stringify(config, null, 2));
}

if (require.main === module) {
  main().catch(err => {
    console.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
}

module.exports = {
  DEFAULTS,
  loadFromEnv,
  loadFromFile,
  getConfig,
  listConfig,
  validateAWS,
  validateAzure,
  validateGCP
};
