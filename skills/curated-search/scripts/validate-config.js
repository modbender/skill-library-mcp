#!/usr/bin/env node
// SECURITY MANIFEST:
//   Environment variables accessed: NONE
//   External endpoints called: NONE
//   Local files read: config.yaml
//   Local files written: NONE
/**
 * Config Validator
 *
 * Validates config.yaml for:
 * - Required fields present
 * - Domain/seeds consistency
 * - Value ranges reasonable
 * - Seed URLs match whitelisted domains
 */

const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

// Parse --config argument to override default config path
let configPath = path.resolve(__dirname, '..', 'config.yaml');
const args = process.argv.slice(2);
const configIdx = args.indexOf('--config');
if (configIdx !== -1 && args[configIdx + 1]) {
  configPath = path.resolve(args[configIdx + 1]);
}

const errors = [];
const warnings = [];

function validate() {
  console.log('Validating configuration...\n');

  // Check file exists
  if (!fs.existsSync(configPath)) {
    errors.push(`Config file not found: ${configPath}`);
    return;
  }

  // Parse YAML
  let config;
  try {
    const yamlStr = fs.readFileSync(configPath, 'utf8');
    config = yaml.parse(yamlStr);
  } catch (e) {
    errors.push(`YAML parse error: ${e.message}`);
    return;
  }

  // Required top-level sections
  const required = ['domains', 'seeds', 'crawl', 'index', 'search'];
  for (const key of required) {
    if (!config[key]) {
      errors.push(`Missing required section: ${key}`);
    }
  }

  // Validate domains
  if (config.domains) {
    if (!Array.isArray(config.domains) || config.domains.length === 0) {
      errors.push('domains must be a non-empty array');
    } else {
      // Check for duplicates
      const unique = new Set(config.domains);
      if (unique.size !== config.domains.length) {
        warnings.push('Duplicate domains detected');
      }

      // Validate domain format (simple check)
      config.domains.forEach((domain, i) => {
        if (!domain.includes('.')) {
          errors.push(`Invalid domain format at index ${i}: ${domain}`);
        }
        if (domain.startsWith('http://') || domain.startsWith('https://')) {
          errors.push(`Domain should NOT include protocol, remove 'https://': ${domain}`);
        }
      });
    }
  }

  // Validate seeds
  if (config.seeds) {
    if (!Array.isArray(config.seeds) || config.seeds.length === 0) {
      errors.push('seeds must be a non-empty array');
    } else {
      // Check each seed URL matches a whitelisted domain
      if (config.domains) {
        config.seeds.forEach((seed, i) => {
          try {
            const url = new URL(seed);
            const hostname = url.hostname;
            
            // Check if this hostname or its parent domain is whitelisted
            const isWhitelisted = config.domains.some(domain => {
              return hostname === domain || hostname.endsWith('.' + domain);
            });
            
            if (!isWhitelisted) {
              errors.push(`Seed ${i} hostname '${hostname}' not in domain whitelist: ${seed}`);
            }
          } catch (e) {
            errors.push(`Invalid URL at seeds[${i}]: ${seed}`);
          }
        });
      }
    }
  }

  // Validate crawl settings
  if (config.crawl) {
    const c = config.crawl;
    
    if (typeof c.depth !== 'number' || c.depth < 0 || c.depth > 5) {
      errors.push('crawl.depth must be a number between 0 and 5');
    }
    
    if (typeof c.delay !== 'number' || c.delay < 0) {
      errors.push('crawl.delay must be a non-negative number (milliseconds)');
    }
    
    if (typeof c.timeout !== 'number' || c.timeout < 1) {
      errors.push('crawl.timeout must be a positive number (seconds)');
    }
    
    if (typeof c.max_documents !== 'number' || c.max_documents < 1) {
      errors.push('crawl.max_documents must be a positive number');
    }
    
    if (typeof c.concurrent_requests !== 'number' || c.concurrent_requests < 1) {
      errors.push('crawl.concurrent_requests must be at least 1');
    }
    
    // Warnings for aggressive settings
    if (c.delay < 500) {
      warnings.push(`crawl.delay is very low (${c.delay}ms) - risk of being blocked`);
    }
    
    if (c.concurrent_requests > 3) {
      warnings.push(`crawl.concurrent_requests is high (${c.concurrent_requests})`);
    }
    
    if (c.depth > 3) {
      warnings.push(`crawl.depth is high (${c.depth}) - will crawl extensively`);
    }
  }

  // Validate index settings
  if (config.index) {
    if (!config.index.path) {
      errors.push('index.path is required');
    }
    
    if (config.index.auto_save_after !== undefined) {
      if (typeof config.index.auto_save_after !== 'number' || config.index.auto_save_after < 0) {
        errors.push('index.auto_save_after must be a non-negative number');
      }
    }
    
    if (config.index.min_content_length !== undefined && config.index.min_content_length < 50) {
      warnings.push('index.min_content_length is very low - may index navigation pages');
    }
  }

  // Validate search settings
  if (config.search) {
    if (config.search.default_limit !== undefined) {
      const dl = config.search.default_limit;
      if (typeof dl !== 'number' || dl < 1 || dl > 100) {
        errors.push('search.default_limit must be between 1 and 100');
      }
    }
    
    if (config.search.max_limit !== undefined) {
      const ml = config.search.max_limit;
      if (typeof ml !== 'number' || ml < 1) {
        errors.push('search.max_limit must be a positive number');
      }
    }

    // Cross-field validation: default_limit <= max_limit
    if (config.search.default_limit !== undefined && config.search.max_limit !== undefined) {
      if (config.search.default_limit > config.search.max_limit) {
        errors.push('search.default_limit cannot exceed search.max_limit');
      }
    }
  }

  // Report results
  console.log('--- Validation Results ---\n');
  
  if (errors.length === 0 && warnings.length === 0) {
    console.log('✅ Configuration is valid!\n');
    console.log(`Domains configured: ${config.domains.length}`);
    console.log(`Seed URLs configured: ${config.seeds.length}`);
    console.log(`Max crawl depth: ${config.crawl.depth}`);
    console.log(`Crawl delay: ${config.crawl.delay}ms`);
    console.log(`Max documents: ${config.crawl.max_documents}`);
    return 0;
  }

  if (errors.length > 0) {
    console.error(`❌ ERRORS (${errors.length}):\n`);
    errors.forEach(e => console.error(`  • ${e}`));
    console.error('');
  }
  
  if (warnings.length > 0) {
    console.error(`⚠️  WARNINGS (${warnings.length}):\n`);
    warnings.forEach(w => console.error(`  • ${w}`));
    console.error('');
  }

  return errors.length > 0 ? 1 : 0;
}

const exitCode = validate();
process.exit(exitCode);
