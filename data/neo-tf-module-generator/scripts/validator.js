#!/usr/bin/env node
/**
 * Terraform Module Validator
 *
 * Usage: node validator.js [--strict] <directory>
 *
 * Example:
 *   node validator.js ./my-module
 *   node validator.js --strict ./generated-module
 *
 * Performs validation:
 *   - Check required files exist (main.tf, variables.tf, outputs.tf)
 *   - HCL syntax validation (using terraform CLI if available, otherwise basic parsing)
 *   - Resource type checking against known Terraform providers
 *   - Best practice checks (no hardcoded values in certain places, etc.)
 *
 * Exit codes:
 *   0 - validation passed
 *   1 - validation failed
 */

const fs = require('fs');
const { exec } = require('child_process');
const path = require('path');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse arguments
const argv = yargs(hideBin(process.argv))
  .option('strict', {
    alias: 's',
    type: 'boolean',
    default: false,
    description: 'Enable strict validation (more rules)'
  })
  .demandCommand(1, 'Directory containing Terraform module is required')
  .argv;

const moduleDir = path.resolve(argv._[0]);
const strict = argv.strict;

/**
 * Run terraform CLI command if available
 */
function runTerraform(args, cwd) {
  return new Promise((resolve, reject) => {
    exec(`terraform ${args}`, {
      cwd,
      env: { ...process.env, TF_INPUT: '0', TF_IN_AUTOMATION: '1' },
      timeout: 30000
    }, (err, stdout, stderr) => {
      if (err) {
        reject({ code: err.code, stdout, stderr });
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

/**
 * Check if terraform CLI is available
 */
async function checkTerraform() {
  try {
    await new Promise((resolve, reject) => {
      exec('terraform version', { timeout: 5000 }, (err, stdout, stderr) => {
        if (err) reject(err);
        else resolve(stdout);
      });
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate required files exist
 */
function checkRequiredFiles(dir) {
  const required = ['main.tf', 'variables.tf', 'outputs.tf'];
  const missing = [];

  for (const file of required) {
    const filePath = path.join(dir, file);
    if (!fs.existsSync(filePath)) {
      missing.push(file);
    }
  }

  return missing;
}

/**
 * Basic HCL syntax validation (without terraform CLI)
 * This is a simplified parser that checks for balanced braces, quotes, etc.
 */
function basicHCLCheck(content, filename) {
  const errors = [];

  // Check for balanced braces
  let braceCount = 0;
  let inString = false;
  let escapeNext = false;

  for (let i = 0; i < content.length; i++) {
    const char = content[i];
    const nextChar = content[i + 1];

    if (escapeNext) {
      escapeNext = false;
      continue;
    }

    if (char === '\\\\') {
      escapeNext = true;
      continue;
    }

    if (char === '"' && !inString) {
      inString = true;
    } else if (char === '"' && inString) {
      inString = false;
    }

    if (!inString) {
      if (char === '{') braceCount++;
      if (char === '}') braceCount--;
    }

    if (braceCount < 0) {
      errors.push(`Unmatched closing brace at ${filename}:${i + 1}`);
      braceCount = 0; // Reset to avoid false positives
    }
  }

  if (braceCount > 0) {
    errors.push(`Unclosed ${braceCount} opening brace(s) in ${filename}`);
  }

  if (inString) {
    errors.push(`Unclosed string literal in ${filename}`);
  }

  // Check for suspicious patterns
  const lines = content.split('\\n');
  lines.forEach((line, idx) => {
    const lineNum = idx + 1;
    const trimmed = line.trim();

    // Check for HEREDOC without closing
    if (trimmed.startsWith('<<') && !trimmed.includes('EOF') && !trimmed.includes('EOT')) {
      // Might be okay with custom delimiter, but check for pattern
    }
  });

  return errors;
}

/**
 * Check resource types against known providers
 */
function checkResourceTypes(files, dir) {
  const errors = [];
  const validProviders = ['aws', 'azurerm', 'google', 'null', 'local', 'random', 'template', 'time', 'kubernetes', 'helm', 'github', 'gitlab'];

  for (const filename of files) {
    if (!filename.endsWith('.tf')) continue;

    const content = fs.readFileSync(path.join(dir, filename), 'utf8');
    const resourceRegex = /resource\\s+"([^"]+)"\\s+"([^"]+)"/g;
    let match;

    while ((match = resourceRegex.exec(content)) !== null) {
      const [full, type] = match;
      const provider = type.split('_')[0];

      if (!validProviders.includes(provider) && !['aws', 'azure', 'gcp', 'google'].includes(provider)) {
        errors.push(`Unknown provider '${provider}' in resource type '${type}' in ${filename}`);
      }

      // Check for common type errors
      if (type.includes('aws_') && !type.match(/^aws_[a-z_]+$/)) {
        errors.push(`Invalid AWS resource type format '${type}' in ${filename}`);
      }
    }
  }

  return errors;
}

/**
 * Check best practices (strict mode)
 */
function checkBestPractices(dir, files) {
  const warnings = [];

  for (const filename of files) {
    if (!filename.endsWith('.tf')) continue;

    const content = fs.readFileSync(path.join(dir, filename), 'utf8');
    const lines = content.split('\\n');

    lines.forEach((line, idx) => {
      const lineNum = idx + 1;

      // Check for hardcoded secrets (very basic)
      if ((line.includes('password') || line.includes('secret') || line.includes('token')) &&
          line.includes('=') &&
          !line.includes('var.') &&
          !line.includes('"')) {
        warnings.push(`${filename}:${lineNum}: Possible hardcoded secret`);
      }

      // Check for use of count/for_each without appropriate conditions
      if (line.includes('count =') || line.includes('for_each =')) {
        const nextLines = lines.slice(idx, idx + 3).join('\\n');
        if (!nextLines.includes('?') && !nextLines.includes('var.')) {
          warnings.push(`${filename}:${lineNum}: Consider using conditional with count/for_each`);
        }
      }
    });
  }

  return warnings;
}

/**
 * Main validation logic
 */
async function validate(dir) {
  const results = {
    valid: true,
    errors: [],
    warnings: [],
    file: null
  };

  // Check directory exists
  if (!fs.existsSync(dir)) {
    results.valid = false;
    results.errors.push(`Directory not found: ${dir}`);
    return results;
  }

  // Check required files
  const missingFiles = checkRequiredFiles(dir);
  if (missingFiles.length > 0) {
    results.valid = false;
    results.errors.push(`Missing required files: ${missingFiles.join(', ')}`);
  }

  // Collect .tf files
  const tfFiles = fs.readdirSync(dir).filter(f => f.endsWith('.tf'));

  if (tfFiles.length === 0 && !missingFiles.includes('main.tf')) {
    results.valid = false;
    results.errors.push('No Terraform configuration files (.tf) found');
  }

  // Validate each file
  for (const file of tfFiles) {
    const filePath = path.join(dir, file);
    const content = fs.readFileSync(filePath, 'utf8');

    // Basic HCL check
    const basicErrors = basicHCLCheck(content, file);
    if (basicErrors.length > 0) {
      results.valid = false;
      results.errors.push(...basicErrors.map(e => `${file}: ${e}`));
    }
  }

  // Check resource types
  const typeErrors = checkResourceTypes(tfFiles, dir);
  if (typeErrors.length > 0) {
    results.valid = false;
    results.errors.push(...typeErrors);
  }

  // Try terraform CLI if available
  const hasTerraform = await checkTerraform();
  if (hasTerraform) {
    try {
      const { stdout, stderr } = await runTerraform('init -backend=false', dir);
      console.error('terraform init succeeded');

      try {
        const validate = await runTerraform('validate -json', dir);
        try {
          const validationResult = JSON.parse(validate.stdout);
          if (!validationResult.valid) {
            results.valid = false;
            for (const diag of validationResult.diagnostics || []) {
              const severity = diag.severity || 'error';
              const message = diag.summary || diag.detail || '';
              const location = diag.range
                ? `${diag.range.filename}:${diag.range.start.line}`
                : 'unknown';

              if (severity === 'error') {
                results.errors.push(`${location}: ${message}`);
              } else {
                results.warnings.push(`${location}: ${message}`);
              }
            }
          } else {
            console.error('terraform validate passed');
          }
        } catch (e) {
          // Non-JSON output (older terraform)
          if (validate.stderr && validate.stderr.includes('Error')) {
            results.valid = false;
            results.errors.push(validate.stderr);
          } else {
            console.error('terraform validate succeeded');
          }
        }
      } catch (e) {
        results.warnings.push(`terraform validate failed: ${e.stderr || e.message}`);
      }

      // Cleanup .terraform directory
      try {
        await new Promise((resolve, reject) => {
          exec('rm -rf .terraform', { cwd: dir, timeout: 5000 }, (err) => {
            if (err) reject(err);
            else resolve();
          });
        });
      } catch {
        // Ignore cleanup errors
      }

    } catch (e) {
      results.warnings.push(`terraform init failed: ${e.stderr || e.message}`);
    }
  } else {
    results.warnings.push('terraform CLI not available, skipping provider-validated checks');
  }

  // Strict mode checks
  if (strict) {
    const strictWarnings = checkBestPractices(dir, tfFiles);
    results.warnings.push(...strictWarnings);
  }

  return results;
}

/**
 * Main entry
 */
async function main() {
  console.error(`Validating Terraform module: ${moduleDir}`);

  const results = await validate(moduleDir);

  console.error('\\nValidation Results:');
  console.error(`Status: ${results.valid ? 'PASS' : 'FAIL'}`);

  if (results.errors.length > 0) {
    console.error('\\nErrors:');
    results.errors.forEach(e => console.error(`  ✗ ${e}`));
  }

  if (results.warnings.length > 0) {
    console.error('\\nWarnings:');
    results.warnings.forEach(w => console.error(`  ⚠ ${w}`));
  }

  if (results.valid && results.warnings.length === 0) {
    console.error('\\n✓ Module is valid and follows best practices');
  } else if (results.valid) {
    console.error('\\n✓ Module is valid (with warnings)');
  } else {
    console.error('\\n✗ Module contains errors');
  }

  process.exit(results.valid ? 0 : 1);
}

if (require.main === module) {
  main().catch(err => {
    console.error(`Fatal: ${err.message}`);
    process.exit(1);
  });
}

module.exports = { validate, basicHCLCheck, checkRequiredFiles, checkResourceTypes };
