#!/usr/bin/env node
/**
 * fetch-docs.js - 抓取项目文档喂给 LLM
 * Usage: node fetch-docs.js <project|url> [options]
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const SCRIPT_DIR = __dirname;
const REGISTRY_PATH = path.join(SCRIPT_DIR, 'docs-registry.json');
const MAX_SIZE = 500_000; // 500KB warning

// Colors
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const BLUE = '\x1b[34m';
const NC = '\x1b[0m';

const log = (msg) => console.error(`${BLUE}[docs]${NC} ${msg}`);
const warn = (msg) => console.error(`${YELLOW}[warn]${NC} ${msg}`);
const error = (msg) => { console.error(`${RED}[error]${NC} ${msg}`); process.exit(1); };
const success = (msg) => console.error(`${GREEN}[ok]${NC} ${msg}`);

// Load registry
function loadRegistry() {
  try {
    return JSON.parse(fs.readFileSync(REGISTRY_PATH, 'utf8'));
  } catch (e) {
    return {};
  }
}

// HTTP fetch with redirects
function fetch(url, maxRedirects = 5) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    
    const req = client.get(url, { timeout: 30000 }, (res) => {
      // Handle redirects
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        if (maxRedirects <= 0) {
          reject(new Error('Too many redirects'));
          return;
        }
        const redirectUrl = new URL(res.headers.location, url).href;
        resolve(fetch(redirectUrl, maxRedirects - 1));
        return;
      }
      
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }
      
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    });
    
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
  });
}

// Try to fetch LLM-friendly docs
async function fetchLlmsTxt(baseUrl, llmsPath = '/llms-full.txt') {
  const paths = [llmsPath];
  if (llmsPath === '/llms-full.txt') {
    paths.push('/llms.txt');
  }
  
  for (const p of paths) {
    const url = baseUrl.replace(/\/$/, '') + p;
    log(`尝试 ${url}`);
    
    try {
      const content = await fetch(url);
      if (content && content.length > 100) {
        return { content, source: url };
      }
    } catch (e) {
      // Try next
    }
  }
  
  return null;
}

// Fetch GitHub README
async function fetchGitHubReadme(repo) {
  log(`Fallback: GitHub README (${repo})`);
  
  const branches = ['main', 'master'];
  for (const branch of branches) {
    const url = `https://raw.githubusercontent.com/${repo}/${branch}/README.md`;
    try {
      const content = await fetch(url);
      if (content) {
        return { content, source: `github:${repo}` };
      }
    } catch (e) {
      // Try next
    }
  }
  
  return null;
}

// Fetch local docs
function fetchLocal(localPath) {
  try {
    if (fs.statSync(localPath).isDirectory()) {
      log(`读取本地文档: ${localPath}`);
      const files = fs.readdirSync(localPath, { recursive: true })
        .filter(f => f.endsWith('.md'));
      
      let content = '';
      for (const file of files) {
        const fullPath = path.join(localPath, file);
        if (fs.statSync(fullPath).isFile()) {
          content += fs.readFileSync(fullPath, 'utf8') + '\n\n';
        }
      }
      return { content, source: `local:${localPath}` };
    } else if (fs.statSync(localPath).isFile()) {
      return { content: fs.readFileSync(localPath, 'utf8'), source: `local:${localPath}` };
    }
  } catch (e) {
    return null;
  }
}

// Format size
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)}MB`;
}

// Main fetch logic
async function fetchDocs(input, options = {}) {
  const registry = loadRegistry();
  let result = null;
  let projectName = input;
  
  // Check if input is URL
  if (input.match(/^https?:\/\//)) {
    projectName = input.replace(/^https?:\/\//, '').split('/')[0].replace(/^www\./, '').split('.')[0];
    result = await fetchLlmsTxt(input);
    if (!result) {
      error(`无法从 ${input} 抓取文档`);
    }
  } else {
    // Lookup in registry
    const config = registry[input];
    
    if (!config) {
      warn(`项目 '${input}' 不在 registry 中，尝试常见模式...`);
      
      const patterns = [
        `https://docs.${input}.com`,
        `https://${input}.dev`,
        `https://${input}.io`,
        `https://www.${input}.com/docs`
      ];
      
      for (const baseUrl of patterns) {
        result = await fetchLlmsTxt(baseUrl);
        if (result) break;
      }
      
      if (!result) {
        error(`找不到 '${input}' 的文档。使用 --list 查看支持的项目。`);
      }
    } else {
      // Try in order: local -> llms.txt -> github
      if (config.local) {
        result = fetchLocal(config.local);
      }
      
      if (!result && config.url) {
        result = await fetchLlmsTxt(config.url, config.llms || '/llms-full.txt');
      }
      
      if (!result && config.github) {
        result = await fetchGitHubReadme(config.github);
      }
      
      if (!result) {
        error(`无法抓取 '${input}' 的文档`);
      }
    }
  }
  
  const { content, source } = result;
  const size = Buffer.byteLength(content, 'utf8');
  
  if (size > MAX_SIZE) {
    warn(`文档较大 (${formatSize(size)})，可能需要裁剪`);
  }
  
  // Output
  if (options.raw) {
    console.log(content);
  } else {
    console.log(`# Documentation: ${projectName}

**Source:** ${source}
**Size:** ${formatSize(size)}
**Fetched:** ${new Date().toISOString()}

---

${content}`);
  }
  
  if (options.save) {
    const outfile = `/tmp/docs-${projectName.replace(/[^a-zA-Z0-9]/g, '-')}.md`;
    fs.writeFileSync(outfile, content);
    success(`已保存到 ${outfile}`);
  } else {
    success(`已抓取 ${projectName} 文档 (${formatSize(size)})`);
  }
}

// List all projects
function listProjects() {
  const registry = loadRegistry();
  console.log('支持的项目：\n');
  const projects = Object.keys(registry).filter(k => !k.startsWith('_')).sort();
  
  // Print in columns
  const cols = 4;
  const rows = Math.ceil(projects.length / cols);
  for (let r = 0; r < rows; r++) {
    let line = '';
    for (let c = 0; c < cols; c++) {
      const idx = c * rows + r;
      if (idx < projects.length) {
        line += projects[idx].padEnd(20);
      }
    }
    console.log(line);
  }
}

// Usage
function usage() {
  console.log(`Usage: node fetch-docs.js <project|url> [options]

Examples:
  node fetch-docs.js nextjs              # 按项目名抓取
  node fetch-docs.js https://hono.dev    # 按 URL 抓取
  node fetch-docs.js react --raw         # 只输出内容，不加元信息
  node fetch-docs.js --list              # 列出所有支持的项目

Options:
  --raw         只输出文档内容
  --save        保存到文件
  --list        列出支持的项目
  --help        显示帮助`);
}

// Main
async function main() {
  const args = process.argv.slice(2);
  const options = {};
  let input = '';
  
  for (const arg of args) {
    switch (arg) {
      case '--help':
      case '-h':
        usage();
        process.exit(0);
      case '--list':
      case '-l':
        listProjects();
        process.exit(0);
      case '--raw':
        options.raw = true;
        break;
      case '--save':
        options.save = true;
        break;
      default:
        if (!arg.startsWith('-')) {
          input = arg;
        }
    }
  }
  
  if (!input) {
    usage();
    process.exit(1);
  }
  
  await fetchDocs(input, options);
}

main().catch(e => error(e.message));
