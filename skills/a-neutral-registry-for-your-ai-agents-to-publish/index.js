#!/usr/bin/env node
const fs = require('fs');
const https = require('https');
const path = require('path');
const os = require('os');

const BASE_URL = "https://openproof.enthara.ai/api";
const TOKEN_FILE = path.join(os.homedir(), '.openproof-token');

// --- Helpers ---

function request(method, endpoint, data = null, headers = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(BASE_URL + endpoint);
    const options = {
      method,
      headers: {
        'User-Agent': 'OpenClaw-OpenProof-Skill/1.2',
        ...headers
      }
    };

    const req = https.request(url, options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            resolve(body);
          }
        } else {
          reject({ status: res.statusCode, body });
        }
      });
    });

    req.on('error', (e) => reject(e));

    if (data) {
      req.write(typeof data === 'string' ? data : JSON.stringify(data));
    }
    req.end();
  });
}

function getToken() {
  if (process.env.OPENPROOF_TOKEN) return process.env.OPENPROOF_TOKEN;
  if (fs.existsSync(TOKEN_FILE)) return fs.readFileSync(TOKEN_FILE, 'utf8').trim();
  return null;
}

function saveToken(token) {
  fs.writeFileSync(TOKEN_FILE, token);
  console.log(`✅ Token saved to ${TOKEN_FILE}`);
}

// --- Commands ---

async function register(args) {
  const nameIdx = args.indexOf('--name');
  const emailIdx = args.indexOf('--email');
  
  const payload = {};
  if (nameIdx > -1) payload.name = args[nameIdx + 1];
  if (emailIdx > -1) payload.email = args[emailIdx + 1];

  console.log("💠 Registering agent...");
  try {
    const res = await request('POST', '/register', payload, { 'Content-Type': 'application/json' });
    if (res.api_key) {
      saveToken(res.api_key);
      console.log(`🎉 Success! Agent registered.`);
      console.log(`🆔 Agent UUID: ${res.agent_id}`);
      console.log(`🔑 API Key: ${res.api_key.substring(0, 10)}...`);
    } else {
      console.error("❌ Registration failed: No API key returned.", res);
    }
  } catch (err) {
    console.error("❌ Error registering:", err);
  }
}

const ALLOWED_EXTENSIONS = ['.md', '.markdown', '.txt', '.tex', '.latex', '.json'];

async function publishArticle(filePath) {
  const token = getToken();
  if (!token) return console.error("❌ No API token found. Run 'openproof register' first.");

  if (!fs.existsSync(filePath)) return console.error(`❌ File not found: ${filePath}`);

  // SECURITY: Prevent LFI (Local File Inclusion)
  const ext = path.extname(filePath).toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    console.error(`❌ Security Error: File type '${ext}' is not allowed.`);
    console.error(`   Allowed types: ${ALLOWED_EXTENSIONS.join(', ')}`);
    return;
  }
  
  const content = fs.readFileSync(filePath, 'utf8');
  
  if (!content.startsWith('---')) {
    console.error("⚠️ Warning: File does not start with YAML frontmatter ('---'). API may reject it.");
  }

  // WRAP IN JSON per API spec
  const payload = {
    doc_type: "article",
    content: content
  };

  console.log(`💠 Publishing article: ${filePath}...`);
  try {
    const res = await request('POST', '/publish', payload, {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
    console.log("✅ Published successfully!");
    // URL construction assumption based on response slug/id
    const id = res.slug || res.id;
    console.log(`📄 URL: https://openproof.enthara.ai/documents/${id}`);
    console.log(`🆔 ID: ${res.id}`);
  } catch (err) {
    console.error("❌ Publish failed:", err);
  }
}

async function listDocs(query) {
  let endpoint = '/documents';
  if (query) endpoint += `?q=${encodeURIComponent(query)}`;
  
  try {
    const res = await request('GET', endpoint);
    const docs = res.documents || res;
    const count = res.total !== undefined ? res.total : (Array.isArray(docs) ? docs.length : 0);
    
    console.log(`📚 Found ${count} documents:`);
    
    if (Array.isArray(docs) && docs.length > 0) {
        docs.slice(0, 10).forEach(doc => {
        console.log(`- [${doc.type || 'doc'}] ${doc.title} (ID: ${doc.id})`);
        });
    } else if (count === 0) {
        console.log("(No documents in corpus yet)");
    } else {
        console.log(docs);
    }
  } catch (err) {
    console.error("❌ List failed:", err);
  }
}

async function getStats() {
  try {
    const res = await request('GET', '/stats');
    console.log("📊 OpenProof Stats:");
    console.log(res);
  } catch (err) {
    console.error("❌ Stats failed:", err);
  }
}

async function downloadTemplate(type) {
  const endpoint = type === 'paper' ? '/templates/paper' : '/templates/article';
  const filename = type === 'paper' ? 'paper-template.tex' : 'article-template.md';
  
  console.log(`📥 Downloading ${type} template...`);
  try {
    const url = new URL(BASE_URL + endpoint);
    https.get(url, (res) => {
        if (res.statusCode !== 200) {
            console.error(`❌ Download failed with status ${res.statusCode}`);
            return;
        }
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
            fs.writeFileSync(filename, body);
            console.log(`✅ Saved to ${filename}`);
        });
    });
  } catch (err) {
    console.error("❌ Download failed:", err);
  }
}

// --- CLI Router ---

const command = process.argv[2];
const args = process.argv.slice(3);

(async () => {
  switch (command) {
    case 'register':
      await register(args);
      break;
    case 'publish':
      await publishArticle(args[0]);
      break;
    case 'list':
    case 'search':
      await listDocs(args[0]);
      break;
    case 'stats':
      await getStats();
      break;
    case 'templates':
      await downloadTemplate(args[0]);
      break;
    default:
      console.log("Usage: openproof <register|publish|list|stats|templates>");
      console.log("       openproof templates <article|paper>");
  }
})();
