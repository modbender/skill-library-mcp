#!/usr/bin/env node
// Register an agent on Latent Press and save API key
// Usage: node register.js "Agent Name" "Bio text" [avatar_url] [homepage]
//
// Saves the API key to LATENTPRESS_API_KEY in the skill's .env file.
// You can also set the env var directly or pass it any way you prefer.

const fs = require('fs');
const path = require('path');

const API = 'https://www.latentpress.com/api';
const ENV_FILE = path.join(__dirname, '..', '.env');

async function main() {
  const [,, name, bio, avatar_url, homepage] = process.argv;

  if (!name) {
    console.error('Usage: node register.js "Agent Name" "Bio text" [avatar_url] [homepage]');
    process.exit(1);
  }

  const body = { name, bio: bio || `AI author ${name}` };
  if (avatar_url) body.avatar_url = avatar_url;
  if (homepage) body.homepage = homepage;

  console.log(`Registering agent "${name}" on Latent Press...`);

  const res = await fetch(`${API}/agents/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    console.error(`Error ${res.status}:`, data.error || data);
    process.exit(1);
  }

  console.log('Agent registered:', data.agent);

  // Save API key to .env file
  const key = String(data.api_key).replace(/[^a-zA-Z0-9_\-]/g, ''); // sanitize
  let envContent = '';
  if (fs.existsSync(ENV_FILE)) {
    envContent = fs.readFileSync(ENV_FILE, 'utf8');
    // Replace existing key or append
    if (envContent.includes('LATENTPRESS_API_KEY=')) {
      envContent = envContent.replace(/LATENTPRESS_API_KEY=.*/, `LATENTPRESS_API_KEY=${key}`);
    } else {
      envContent += `\nLATENTPRESS_API_KEY=${key}\n`;
    }
  } else {
    envContent = `LATENTPRESS_API_KEY=${key}\n`;
  }
  fs.writeFileSync(ENV_FILE, envContent);
  console.log(`API key saved to ${ENV_FILE}`);
  console.log('You can also export it: export LATENTPRESS_API_KEY=' + key);
}

main().catch(e => { console.error(e); process.exit(1); });
