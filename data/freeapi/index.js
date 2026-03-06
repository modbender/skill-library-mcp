#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { program } from 'commander';
import dotenv from 'dotenv';
import YAML from 'yaml';
import inquirer from 'inquirer';

// Load environment variables from .env file
dotenv.config();

const SERVICES = [
  { name: 'GitHub', key: 'GITHUB_TOKEN' },
  { name: 'OpenAI', key: 'OPENAI_API_KEY' },
  { name: 'Anthropic (Claude)', key: 'ANTHROPIC_API_KEY' },
  { name: 'Google Search Console', key: 'GOOGLE_SEARCH_CONSOLE_KEY' },
  { name: 'Firebase', key: 'FIREBASE_API_KEY' },
  { name: 'Netlify', key: 'NETLIFY_AUTH_TOKEN' },
  { name: 'Vercel', key: 'VERCEL_TOKEN' },
  { name: 'ElevenLabs', key: 'ELEVENLABS_API_KEY' },
  { name: 'Beehiiv', key: 'BEEHIIV_API_KEY' },
  { name: 'WordPress', key: 'WORDPRESS_API_KEY' },
  { name: 'Ghost', key: 'GHOST_ADMIN_API_KEY' },
  { name: 'Dropbox', key: 'DROPBOX_ACCESS_TOKEN' },
  { name: 'Google Drive', key: 'GOOGLE_DRIVE_API_KEY' },
  { name: 'Gmail', key: 'GMAIL_API_KEY' },
  { name: 'Vimeo', key: 'VIMEO_ACCESS_TOKEN' },
  { name: 'YouTube', key: 'YOUTUBE_API_KEY' },
  { name: 'Gumroad', key: 'GUMROAD_ACCESS_TOKEN' },
  { name: 'Stripe', key: 'STRIPE_SECRET_KEY' },
  { name: 'Shopify', key: 'SHOPIFY_ACCESS_TOKEN' },
  { name: 'Notion', key: 'NOTION_API_KEY' },
  { name: 'Slack', key: 'SLACK_BOT_TOKEN' },
  { name: 'Discord', key: 'DISCORD_BOT_TOKEN' },
  { name: 'DigitalOcean', key: 'DIGITALOCEAN_ACCESS_TOKEN' },
  { name: 'Brave Search', key: 'BRAVE_SEARCH_API_KEY' },
  { name: 'Hugging Face', key: 'HUGGING_FACE_TOKEN' },
  { name: 'Stability AI', key: 'STABILITY_API_KEY' },
  { name: 'Twitter/X', key: 'TWITTER_BEARER_TOKEN' }
];

const loadSpec = async (specPath) => {
  let content;
  if (specPath.startsWith('http')) {
    const res = await fetch(specPath);
    if (!res.ok) throw new Error(`Failed to fetch spec: ${res.statusText}`);
    content = await res.text();
  } else {
    content = fs.readFileSync(specPath, 'utf8');
  }

  try {
    return JSON.parse(content);
  } catch {
    try {
      return YAML.parse(content);
    } catch {
      throw new Error('Failed to parse spec as JSON or YAML');
    }
  }
};

const resolveRef = (ref, spec) => {
  const parts = ref.replace(/^#\//, '').split('/');
  let current = spec;
  for (const part of parts) {
    current = current[part];
  }
  return current;
};

const listOperations = (spec) => {
  const operations = [];
  for (const [pathKey, pathItem] of Object.entries(spec.paths || {})) {
    for (const [method, op] of Object.entries(pathItem)) {
      if (['get', 'post', 'put', 'delete', 'patch'].includes(method)) {
        operations.push({
          method: method.toUpperCase(),
          path: pathKey,
          operationId: op.operationId || `${method}_${pathKey}`,
          summary: op.summary || 'No summary',
        });
      }
    }
  }
  return operations;
};

const executeRequest = async (spec, operationId, params = {}, body = {}) => {
  let selectedOp = null;
  let selectedPath = null;
  let selectedMethod = null;

  // Find the operation
  for (const [pathKey, pathItem] of Object.entries(spec.paths || {})) {
    for (const [method, op] of Object.entries(pathItem)) {
      if (op.operationId === operationId || `${method}_${pathKey}` === operationId) {
        selectedOp = op;
        selectedPath = pathKey;
        selectedMethod = method;
        break;
      }
    }
    if (selectedOp) break;
  }

  if (!selectedOp) throw new Error(`Operation ${operationId} not found`);

  // Build URL
  let url = spec.servers?.[0]?.url || 'http://localhost';
  if (!url.startsWith('http')) url = `https://${url}`; // Default to https if relative or missing protocol

  // Replace path params
  let finalPath = selectedPath;
  if (selectedOp.parameters) {
    for (const param of selectedOp.parameters) {
        const p = param.$ref ? resolveRef(param.$ref, spec) : param;
        if (p.in === 'path') {
            const val = params[p.name];
            if (!val) throw new Error(`Missing path parameter: ${p.name}`);
            finalPath = finalPath.replace(`{${p.name}}`, val);
        }
    }
  }

  // Add query params
  const queryParams = new URLSearchParams();
  if (selectedOp.parameters) {
      for (const param of selectedOp.parameters) {
          const p = param.$ref ? resolveRef(param.$ref, spec) : param;
          if (p.in === 'query' && params[p.name]) {
              queryParams.append(p.name, params[p.name]);
          }
      }
  }

  const fullUrl = `${url}${finalPath}${queryParams.toString() ? '?' + queryParams.toString() : ''}`;

  // Headers (Auth + Content-Type)
  const headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Maton/1.0 (OpenClaw)',
  };

  // Simple Auth Injection (Bearer/API Key from ENV)
  // This is a heuristic: match security scheme names to ENV vars
  if (spec.components?.securitySchemes) {
      for (const [schemeName, scheme] of Object.entries(spec.components.securitySchemes)) {
          const envVarName = schemeName.toUpperCase().replace(/[^A-Z0-9]/g, '_'); // e.g., api_key -> API_KEY
          const token = process.env[envVarName] || process.env[`${envVarName}_TOKEN`] || process.env[`${envVarName}_KEY`];
          
          if (token) {
              if (scheme.type === 'http' && scheme.scheme === 'bearer') {
                  headers['Authorization'] = `Bearer ${token}`;
              } else if (scheme.type === 'apiKey' && scheme.in === 'header') {
                  headers[scheme.name] = token;
              }
          }
      }
  }

  console.error(`Executing ${selectedMethod.toUpperCase()} ${fullUrl}`); // Log to stderr to keep stdout clean for JSON output

  const res = await fetch(fullUrl, {
    method: selectedMethod,
    headers,
    body: ['POST', 'PUT', 'PATCH'].includes(selectedMethod.toUpperCase()) ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
};

program
  .name('freeapi')
  .description('Bare metal OpenAPI client')
  .version('1.0.0');

program
  .command('list')
  .description('List available operations in a spec')
  .requiredOption('-s, --spec <path>', 'Path or URL to OpenAPI spec')
  .action(async (options) => {
    try {
      const spec = await loadSpec(options.spec);
      const ops = listOperations(spec);
      console.table(ops.map(o => ({ Method: o.method, ID: o.operationId, Summary: o.summary.substring(0, 50) })));
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
  });

program
  .command('run')
  .description('Execute an operation')
  .requiredOption('-s, --spec <path>', 'Path or URL to OpenAPI spec')
  .requiredOption('-o, --operation <id>', 'Operation ID to execute')
  .option('-p, --params <json>', 'Path/Query parameters as JSON string', '{}')
  .option('-b, --body <json>', 'Request body as JSON string', '{}')
  .action(async (options) => {
    try {
      const spec = await loadSpec(options.spec);
      const params = JSON.parse(options.params);
      const body = JSON.parse(options.body);
      const result = await executeRequest(spec, options.operation, params, body);
      console.log(JSON.stringify(result, null, 2));
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
  });

program
  .command('setup')
  .description('Interactive setup for API keys (updates .env)')
  .action(async () => {
    console.log('--- freeAPI Setup ---');
    console.log('Select services to configure (Space to select, Enter to confirm):');

    const { selectedServices } = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'selectedServices',
        message: 'Select services:',
        choices: SERVICES.map(s => ({ name: s.name, value: s })),
        pageSize: 15
      }
    ]);

    if (selectedServices.length === 0) {
      console.log('No services selected. Exiting.');
      return;
    }

    console.log('\n--- Configuring Keys ---');
    
    const envPath = path.resolve(process.cwd(), '.env');
    let envContent = '';
    if (fs.existsSync(envPath)) {
      envContent = fs.readFileSync(envPath, 'utf8');
    }

    for (const service of selectedServices) {
      const { key } = await inquirer.prompt([
        {
          type: 'password',
          name: 'key',
          message: `Enter API Key for ${service.name} (${service.key}):`,
          mask: '*'
        }
      ]);

      if (key) {
        // Simple append, could be smarter about replacing existing keys
        if (!envContent.includes(`${service.key}=`)) {
            fs.appendFileSync(envPath, `\n${service.key}=${key}`);
            console.log(`Saved ${service.key} to .env`);
        } else {
            console.log(`${service.key} already exists in .env. Skipping.`);
        }
      }
    }
    
    console.log('\nSetup complete! You can now use freeAPI with these services.');
  });

program.parse();
