/**
 * SealVera autoload — zero-friction intercept via NODE_OPTIONS
 *
 * Usage (no code changes needed):
 *   export NODE_OPTIONS="--require sealvera/autoload"
 *
 * Or in OpenClaw config (openclaw.json):
 *   { "env": { "NODE_OPTIONS": "--require sealvera/autoload" } }
 *
 * Required env vars:
 *   SEALVERA_API_KEY   — your SealVera API key (sv_...)
 *
 * Optional:
 *   SEALVERA_ENDPOINT  — default: https://app.sealvera.com
 *   SEALVERA_AGENT     — agent name shown in dashboard (default: openclaw-agent)
 *   SEALVERA_AUTO_REASONING — set to 'false' to disable (default: on)
 *   SEALVERA_SILENT    — set to '1' to suppress startup log line
 */
'use strict';

const path = require('path');
const fs   = require('fs');

const API_KEY  = process.env.SEALVERA_API_KEY;
const ENDPOINT = (process.env.SEALVERA_ENDPOINT || 'https://app.sealvera.com').replace(/\/$/, '');
const AGENT    = process.env.SEALVERA_AGENT || 'openclaw-agent';
const SILENT   = process.env.SEALVERA_SILENT === '1';
const AUTO_R   = process.env.SEALVERA_AUTO_REASONING !== 'false';

// Load config file if present (.sealvera.json in cwd)
let fileConfig = {};
try {
  const cfgPath = path.join(process.cwd(), '.sealvera.json');
  if (fs.existsSync(cfgPath)) fileConfig = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
} catch(_) {}

const resolvedKey      = API_KEY      || fileConfig.apiKey      || '';
const resolvedEndpoint = ENDPOINT     || fileConfig.endpoint    || 'https://app.sealvera.com';
const resolvedAgent    = AGENT        || fileConfig.agent       || 'openclaw-agent';
const resolvedAutoR    = AUTO_R && fileConfig.autoReasoning !== false;

// Bail silently if no API key — don't break the agent
if (!resolvedKey) {
  if (!SILENT) process.stderr.write('[SealVera] autoload: SEALVERA_API_KEY not set — skipping\n');
  return;
}

// Resolve SDK path — try require.resolve, then local node_modules, then sibling workspace
function findSdk() {
  const candidates = [
    () => require.resolve('sealvera'),
    () => path.join(process.cwd(), 'node_modules', 'sealvera', 'index.js'),
    () => path.join(__dirname, '..', '..', '..', 'sealvera-sdk', 'index.js'),
    () => path.join(__dirname, 'node_modules', 'sealvera', 'index.js'),
  ];
  for (const c of candidates) {
    try {
      const p = c();
      if (fs.existsSync(p)) return p;
    } catch(_) {}
  }
  return null;
}

const sdkPath = findSdk();
if (!sdkPath) {
  if (!SILENT) process.stderr.write('[SealVera] autoload: SDK not found — run: npm install sealvera\n');
  return;
}

let SealVera;
try {
  SealVera = require(sdkPath);
} catch(e) {
  if (!SILENT) process.stderr.write(`[SealVera] autoload: SDK load failed — ${e.message}\n`);
  return;
}

// Init SDK
try {
  SealVera.init({
    endpoint:      resolvedEndpoint,
    apiKey:        resolvedKey,
    autoReasoning: resolvedAutoR,
  });
} catch(e) {
  if (!SILENT) process.stderr.write(`[SealVera] autoload: init failed — ${e.message}\n`);
  return;
}

// Intercept strategy: hook Module._resolveFilename to patch SDKs as they load
const Module = require('module');
const _origResolve = Module._resolveFilename.bind(Module);
const _patched = new Set();

Module._resolveFilename = function(request, parent, isMain, options) {
  const resolved = _origResolve(request, parent, isMain, options);

  // Patch OpenAI / OpenRouter when first loaded
  if (!_patched.has('openai') && (request === 'openai' || resolved.includes('/openai/'))) {
    _patched.add('openai');
    setImmediate(() => {
      try {
        const { OpenAI } = require('openai');
        if (OpenAI && !OpenAI.__sealvera) {
          // Detect OpenRouter by baseURL
          const proto = OpenAI.prototype;
          const origInit = proto.constructor;
          // Patch every new OpenAI instance at construction time
          const OrigOpenAI = OpenAI;
          function PatchedOpenAI(cfg) {
            const instance = new OrigOpenAI(cfg);
            const isOR = cfg?.baseURL?.includes('openrouter');
            try {
              if (isOR) SealVera.patchOpenRouter(instance, { agent: resolvedAgent });
              else       SealVera.patchOpenAI(instance,    { agent: resolvedAgent });
            } catch(_) {}
            return instance;
          }
          PatchedOpenAI.prototype = OrigOpenAI.prototype;
          PatchedOpenAI.__sealvera = true;
          // Overwrite in require cache
          const mod = require.cache[require.resolve('openai')];
          if (mod) { mod.exports.OpenAI = PatchedOpenAI; mod.exports.default = PatchedOpenAI; }
        }
      } catch(_) {}
    });
  }

  // Patch Anthropic when first loaded
  if (!_patched.has('anthropic') && (request === '@anthropic-ai/sdk' || resolved.includes('@anthropic-ai'))) {
    _patched.add('anthropic');
    setImmediate(() => {
      try {
        const Anthropic = require('@anthropic-ai/sdk');
        const A = Anthropic?.default || Anthropic?.Anthropic || Anthropic;
        if (A && !A.__sealvera) {
          const OrigA = A;
          function PatchedAnthropic(cfg) {
            const instance = new OrigA(cfg);
            try { SealVera.patchAnthropic(instance, { agent: resolvedAgent }); } catch(_) {}
            return instance;
          }
          PatchedAnthropic.prototype = OrigA.prototype;
          PatchedAnthropic.__sealvera = true;
          const mod = require.cache[require.resolve('@anthropic-ai/sdk')];
          if (mod) {
            if (mod.exports.default)    mod.exports.default    = PatchedAnthropic;
            if (mod.exports.Anthropic)  mod.exports.Anthropic  = PatchedAnthropic;
            else                        mod.exports             = PatchedAnthropic;
          }
        }
      } catch(_) {}
    });
  }

  return resolved;
};

// Also patch any already-loaded SDKs (if autoload.js is required after them)
setImmediate(() => {
  try {
    const openaiMod = require.cache[require.resolve('openai')];
    if (openaiMod && !openaiMod.exports.OpenAI?.__sealvera) {
      const inst = new openaiMod.exports.OpenAI({ apiKey: 'dummy' });
      SealVera.patchOpenAI(inst, { agent: resolvedAgent });
      if (!SILENT) process.stderr.write(`[SealVera] autoload: patched existing OpenAI instance\n`);
    }
  } catch(_) {}
  try {
    const antMod = require.cache[require.resolve('@anthropic-ai/sdk')];
    if (antMod && !antMod.exports.__sealvera) {
      const A = antMod.exports?.default || antMod.exports?.Anthropic || antMod.exports;
      if (A) {
        const inst = new A({ apiKey: 'dummy' });
        SealVera.patchAnthropic(inst, { agent: resolvedAgent });
        if (!SILENT) process.stderr.write(`[SealVera] autoload: patched existing Anthropic instance\n`);
      }
    }
  } catch(_) {}
});

if (!SILENT) {
  process.stderr.write(`[SealVera] autoload: active — agent="${resolvedAgent}" endpoint="${resolvedEndpoint}"\n`);
}
