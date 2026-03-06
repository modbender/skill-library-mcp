import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import crypto from 'crypto';
import path from 'path';
import fs from 'fs';
import { config } from './config';
import { startOracle, getCostSurface, isOracleHealthy } from './services/energy-oracle';
import { startAttestationBatcher, getAttestationStats } from './services/eas-attestation';
import { getStats } from './services/free-tier';
import { getNodeHealth } from './services/spatial-router';
import { getEthBalance, getUsdcBalance } from './services/payment';
import { createApiKey, getKeyInfo, getKeysByWallet, extractApiKey, validateApiKey, deleteApiKey, purgeInactiveKeys, anonymizeOldRequests } from './services/api-keys';
import { ethers } from 'ethers';
import { checkIdentity, TIER_FREE_REQUESTS } from './services/onchain-identity';
import { getCacheStats, purgeExpired } from './services/cache';
import { createCheckoutSession, handleWebhook, TOP_UP_AMOUNTS } from './services/stripe';
import { startUsdcWatcher } from './services/usdc-watcher';
import { startEthWatcher } from './services/eth-watcher';
import inferenceRouter from './routes/inference';
import { startAcpHandler } from './services/acp-handler';

const app = express();

// H7: Trust proxy (running behind nginx/Cloudflare) — needed for accurate req.ip in rate limiters
app.set('trust proxy', 1);

// H3: Restrict CORS to known origins
app.use(cors({
  origin: ['https://windfall.ecofrontiers.xyz', 'https://ecofrontiers.xyz'],
  credentials: true,
  exposedHeaders: ['X-Windfall-Cache', 'X-Windfall-Mode', 'X-Windfall-Model', 'X-Windfall-Engagement', 'X-Windfall-Node', 'X-Windfall-Cost', 'X-Windfall-Saved', 'PAYMENT-REQUIRED', 'PAYMENT-RESPONSE'],
}));

// H4: Enable Content Security Policy
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://js.stripe.com"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.stripe.com"],
      frameSrc: ["https://js.stripe.com"],
    },
  },
}));

// --- Rate Limiters ---

const apiLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 60,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests — limit is 60/min for inference.' },
});

const keyCreationLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many key creation requests — limit is 5/hour.' },
});

const generalLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 120,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests — limit is 120/min.' },
});

// M1: Strict contact form rate limiter
const contactLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many contact submissions — limit is 3/hour.' },
});

// M6: Dashboard login rate limiter (brute-force protection)
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many login attempts — try again in 15 minutes.' },
});

// --- Dashboard Session Management (defined early so /api/stats can use it) ---

// H9: Session tokens with expiry (Map<token, expiresAt>)
const dashboardSessions = new Map<string, number>();
const SESSION_MAX_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours

function isValidSession(token: string | undefined): boolean {
  if (!token) return false;
  const expiresAt = dashboardSessions.get(token);
  if (!expiresAt) return false;
  if (Date.now() > expiresAt) {
    dashboardSessions.delete(token);
    return false;
  }
  return true;
}

function parseCookies(cookieHeader: string | undefined): Record<string, string> {
  const cookies: Record<string, string> = {};
  if (!cookieHeader) return cookies;
  cookieHeader.split(';').forEach(pair => {
    const [key, ...rest] = pair.trim().split('=');
    if (key) cookies[key.trim()] = rest.join('=').trim();
  });
  return cookies;
}

// Periodically clean up expired sessions (every 10 minutes)
setInterval(() => {
  const now = Date.now();
  for (const [token, expiresAt] of dashboardSessions) {
    if (now > expiresAt) dashboardSessions.delete(token);
  }
  for (const [token, session] of walletSessions) {
    if (now > session.expiresAt) walletSessions.delete(token);
  }
}, 10 * 60 * 1000);

// --- Wallet Auth Sessions (SIWE/SIWA — for dashboard + inference) ---

import { walletSessions, getWalletSession } from './services/sessions';
export { walletSessions, getWalletSession };
const walletNonces = new Map<string, number>(); // nonce -> created timestamp

// Rate limiter for wallet auth
const walletAuthLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many auth attempts — try again in 15 minutes.' },
});

// --- Stripe Webhook (needs raw body — MUST be before express.json() and general limiter) ---

app.post('/api/webhooks/stripe', express.raw({ type: 'application/json' }), async (req, res) => {
  try {
    const sig = req.headers['stripe-signature'] as string;
    const result = await handleWebhook(req.body, sig);
    console.log(`[stripe] Webhook: ${result.event}, handled: ${result.handled}`);
    res.json({ received: true, ...result });
  } catch (err: any) {
    console.error('[stripe] Webhook error:', err.message);
    res.status(400).json({ error: 'Webhook processing failed' });
  }
});

// --- General rate limiter (after Stripe webhook so webhooks aren't limited) ---

app.use(generalLimiter);

// --- JSON body parser for everything else ---

app.use(express.json({ limit: '1mb' }));

// --- Health & Status ---

app.get('/health', (_req, res) => {
  const oracleHealthy = isOracleHealthy();
  res.json({
    status: oracleHealthy ? 'healthy' : 'degraded',
    node: config.nodeId,
    location: config.nodeLocation,
    oracle: oracleHealthy ? 'ok' : 'stale',
    uptime: process.uptime(),
    version: '0.1.0',
  });
});

// H2: Cache OpenRouter health check (don't call on every /status request)
let cachedOpenRouterHealth = { healthy: true, detail: 'Reachable', lastChecked: 0 };
const OR_HEALTH_CACHE_MS = 60 * 1000; // 1 minute

async function checkOpenRouterHealth(): Promise<{ healthy: boolean; detail: string }> {
  if (Date.now() - cachedOpenRouterHealth.lastChecked < OR_HEALTH_CACHE_MS) {
    return { healthy: cachedOpenRouterHealth.healthy, detail: cachedOpenRouterHealth.detail };
  }
  try {
    const r = await fetch('https://openrouter.ai/api/v1/models', {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${config.openrouterApiKey}` },
      signal: AbortSignal.timeout(5000),
    });
    cachedOpenRouterHealth = {
      healthy: r.ok,
      detail: r.ok ? 'Reachable' : `HTTP ${r.status}`,
      lastChecked: Date.now(),
    };
  } catch {
    cachedOpenRouterHealth = { healthy: false, detail: 'Unreachable', lastChecked: Date.now() };
  }
  return { healthy: cachedOpenRouterHealth.healthy, detail: cachedOpenRouterHealth.detail };
}

app.get('/status', async (_req, res) => {
  const surface = getCostSurface();
  const attestations = getAttestationStats();
  const nodeHealth = getNodeHealth();

  // --- Dependency health checks (parallel) ---
  const oracleHealthy = isOracleHealthy();

  const [walletResult, openrouterResult, dbResult] = await Promise.allSettled([
    // Wallet / RPC check
    Promise.all([getEthBalance(), getUsdcBalance()]).then(([eth, usdc]) => ({ eth, usdc, healthy: true })),
    // OpenRouter reachability (cached — avoids exposing API key on every request)
    checkOpenRouterHealth(),
    // Database check
    Promise.resolve().then(() => {
      const { getKeyInfoById } = require('./services/api-keys');
      getKeyInfoById(1); // lightweight read
      return { healthy: true };
    }),
  ]);

  const deps = {
    oracle: { healthy: oracleHealthy, detail: oracleHealthy ? 'Electricity Maps polling OK' : 'Stale data (>15min)' },
    openrouter: {
      healthy: openrouterResult.status === 'fulfilled' && openrouterResult.value.healthy,
      detail: openrouterResult.status === 'fulfilled' ? openrouterResult.value.detail : 'Unreachable',
    },
    database: {
      healthy: dbResult.status === 'fulfilled' && dbResult.value.healthy,
      detail: dbResult.status === 'fulfilled' ? 'OK' : 'Unreachable',
    },
    rpc: {
      healthy: walletResult.status === 'fulfilled' && walletResult.value.healthy,
      detail: walletResult.status === 'fulfilled' ? 'Base RPC OK' : 'Base RPC unreachable',
    },
  };

  const allHealthy = Object.values(deps).every(d => d.healthy);
  const anyDown = Object.values(deps).some(d => !d.healthy);
  const criticalDown = !deps.openrouter.healthy || !deps.database.healthy;

  const systemStatus = criticalDown ? 'down' : anyDown ? 'degraded' : 'healthy';

  const ethBalance = walletResult.status === 'fulfilled' ? walletResult.value.eth : 0;
  const usdcBalance = walletResult.status === 'fulfilled' ? walletResult.value.usdc : 0;

  res.json({
    gateway: 'Windfall',
    version: '0.1.0',
    system: {
      status: systemStatus,
      dependencies: deps,
    },
    node: {
      id: config.nodeId,
      location: config.nodeLocation,
      lat: config.nodeLat,
      lon: config.nodeLon,
    },
    oracle: {
      healthy: oracleHealthy,
      lastUpdated: surface.lastUpdated,
      cheapestLocation: surface.cheapestLocation,
      greenestLocation: surface.greenestLocation,
      locations: surface.locations,
    },
    pricing: {
      default: config.pricePerRequest,
      premium: config.premiumPricePerRequest,
      greenSurcharge: `${config.greenSurcharge * 100}%`,
      currency: 'USD',
      accepts: ['card', 'ETH', 'USDC', 'x402'],
    },
    wallet: {
      address: config.walletAddress,
      ethBalance,
      usdcBalance,
    },
    attestations,
    nodeHealth,
    routing: {
      modes: ['cheapest', 'greenest', 'balanced'],
      defaultMode: 'greenest',
    },
    defaultModel: config.defaultModel,
  });
});

// --- API Stats (for admin command center — requires dashboard auth) ---

app.get('/api/stats', (req, res) => {
  // H8: Protect stats behind dashboard authentication
  if (config.dashboardPassword) {
    const cookies = parseCookies(req.headers.cookie);
    const sessionToken = cookies['wf_admin_session'];
    if (!isValidSession(sessionToken)) {
      return res.status(401).json({ error: 'Admin authentication required' });
    }
  }

  try {
    const stats = getStats();
    const surface = getCostSurface();
    const attestations = getAttestationStats();
    const cache = getCacheStats();

    res.json({
      ...stats,
      oracle: {
        healthy: isOracleHealthy(),
        lastUpdated: surface.lastUpdated,
        cheapestLocation: surface.cheapestLocation,
        greenestLocation: surface.greenestLocation,
        locations: surface.locations,
      },
      attestations,
      cache,
    });
  } catch (err: any) {
    console.error('[stats] Error:', err.message);
    res.status(500).json({ error: 'Failed to load stats' });
  }
});

// --- Contact Form ---

app.post('/api/contact', contactLimiter, (req, res) => {
  try {
    const { name, email, location, message } = req.body || {};
    if (!name || !email) {
      return res.status(400).json({ error: 'Name and email are required' });
    }
    // M1: Validate field lengths and email format
    const nameStr = String(name).slice(0, 200);
    const emailStr = String(email).slice(0, 200);
    const locationStr = String(location || '').slice(0, 200);
    const messageStr = String(message || '').slice(0, 2000);

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailStr)) {
      return res.status(400).json({ error: 'Invalid email format' });
    }

    const entry = {
      timestamp: new Date().toISOString(),
      name: nameStr,
      email: emailStr,
      location: locationStr,
      message: messageStr,
    };
    const logPath = path.resolve(__dirname, '../data/contact.jsonl');
    fs.mkdirSync(path.dirname(logPath), { recursive: true });
    fs.appendFileSync(logPath, JSON.stringify(entry) + '\n');
    console.log(`[contact] New inquiry from ${nameStr.slice(0, 50)}`);
    res.json({ ok: true });
  } catch (err: any) {
    console.error('[contact] Error:', err.message);
    res.status(500).json({ error: 'Failed to save' });
  }
});

// --- API Key Management ---

app.post('/api/keys', keyCreationLimiter, async (req, res) => {
  try {
    const { wallet_address, label } = req.body || {};

    // Check onchain identity to determine free request tier
    const identity = await checkIdentity(wallet_address);

    const result = createApiKey(
      wallet_address,
      label,
      identity.tier,
      identity.freeRequests,
    );

    res.status(201).json({
      key: result.key,
      message: 'Save this key — it cannot be retrieved later.',
      free_requests: result.info.freeRequestsRemaining,
      identity_tier: identity.tier,
      tier_info: {
        anonymous: `${TIER_FREE_REQUESTS.anonymous} free requests`,
        wallet: `${TIER_FREE_REQUESTS.wallet} free requests (provide wallet_address)`,
        basename: `${TIER_FREE_REQUESTS.basename} free requests (register a Basename)`,
        erc8004: `${TIER_FREE_REQUESTS.erc8004} free requests (register on Base agent registry)`,
      },
      usage: 'Add header: Authorization: Bearer ' + result.key,
      defaults: {
        routing_mode: 'greenest',
        model: 'auto (DeepSeek V3 for most tasks)',
        override: 'Set "mode" in body or X-Routing-Mode header. Set "model" to use a specific model.',
      },
      info: result.info,
    });
  } catch (err: any) {
    console.error('[keys] Create error:', err.message);
    res.status(500).json({ error: 'Failed to create API key' });
  }
});

app.get('/api/keys/me', (req, res) => {
  try {
    const apiKey = extractApiKey(req.headers as Record<string, string | string[] | undefined>);
    if (!apiKey) {
      return res.status(401).json({ error: 'Include Authorization: Bearer wf_YOUR_KEY header' });
    }
    const info = getKeyInfo(apiKey);
    if (!info) {
      return res.status(404).json({ error: 'API key not found' });
    }
    res.json(info);
  } catch (err: any) {
    console.error('[keys] Info error:', err.message);
    res.status(500).json({ error: 'Failed to retrieve key info' });
  }
});

app.delete('/api/keys/me', (req, res) => {
  try {
    const apiKey = extractApiKey(req.headers as Record<string, string | string[] | undefined>);
    if (!apiKey) {
      return res.status(401).json({ error: 'Include Authorization: Bearer wf_YOUR_KEY header' });
    }
    const deleted = deleteApiKey(apiKey);
    if (!deleted) {
      return res.status(404).json({ error: 'API key not found' });
    }
    res.json({ deleted: true });
  } catch (err: any) {
    console.error('[keys] Delete error:', err.message);
    res.status(500).json({ error: 'Failed to delete key' });
  }
});

// --- Wallet Auth (SIWE — for user dashboard) ---

// Step 1: Get a nonce for SIWE message
app.get('/api/auth/nonce', (_req, res) => {
  const nonce = crypto.randomBytes(16).toString('hex');
  walletNonces.set(nonce, Date.now());
  // Clean up old nonces (>5 min)
  const fiveMinAgo = Date.now() - 5 * 60 * 1000;
  for (const [n, ts] of walletNonces) {
    if (ts < fiveMinAgo) walletNonces.delete(n);
  }
  res.json({ nonce });
});

// Step 2: Verify SIWE signature and create session
app.post('/api/auth/wallet', walletAuthLimiter, async (req, res) => {
  try {
    const { address, signature, message, nonce } = req.body || {};

    if (!address || !signature || !message || !nonce) {
      return res.status(400).json({ error: 'address, signature, message, and nonce are required' });
    }

    // Validate address format
    if (!/^0x[a-fA-F0-9]{40}$/.test(address)) {
      return res.status(400).json({ error: 'Invalid wallet address' });
    }

    // Verify nonce was issued by us and is fresh
    const nonceTs = walletNonces.get(nonce);
    if (!nonceTs || Date.now() - nonceTs > 5 * 60 * 1000) {
      return res.status(400).json({ error: 'Invalid or expired nonce' });
    }
    walletNonces.delete(nonce);

    // Verify the message contains the nonce
    if (!message.includes(nonce)) {
      return res.status(400).json({ error: 'Message does not contain the expected nonce' });
    }

    // Verify signature
    const recovered = ethers.verifyMessage(message, signature);
    if (recovered.toLowerCase() !== address.toLowerCase()) {
      return res.status(401).json({ error: 'Signature verification failed' });
    }

    // Check onchain identity (ERC-8004, Basename) to tag session
    const identity = await checkIdentity(address);

    // Create session
    const token = crypto.randomBytes(32).toString('hex');
    walletSessions.set(token, {
      walletAddress: address.toLowerCase(),
      expiresAt: Date.now() + SESSION_MAX_AGE_MS,
      isAgent: identity.tier === 'erc8004',
      identityTier: identity.tier,
    });

    const sessionType = identity.tier === 'erc8004' ? 'agent (SIWA)' : 'wallet (SIWE)';
    console.log(`[auth] ${sessionType} login: ${address.slice(0, 10)}... [${identity.tier}]`);
    res.json({
      token,
      expiresAt: Date.now() + SESSION_MAX_AGE_MS,
      isAgent: identity.tier === 'erc8004',
      identityTier: identity.tier,
      freeRequests: identity.freeRequests,
    });
  } catch (err: any) {
    console.error('[auth] Wallet auth error:', err.message);
    res.status(500).json({ error: 'Authentication failed' });
  }
});

// Get all keys for authenticated wallet
app.get('/api/keys/by-wallet', (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader?.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Authorization: Bearer <session_token> required' });
    }
    const token = authHeader.slice(7);
    const session = walletSessions.get(token);
    if (!session || Date.now() > session.expiresAt) {
      if (session) walletSessions.delete(token);
      return res.status(401).json({ error: 'Session expired — please sign in again' });
    }

    const keys = getKeysByWallet(session.walletAddress);

    // Aggregate stats across all keys
    const aggregate = {
      walletAddress: session.walletAddress,
      totalKeys: keys.length,
      totalBalanceUsd: keys.reduce((s, k) => s + k.balanceUsd, 0),
      totalFreeRemaining: keys.reduce((s, k) => s + k.freeRequestsRemaining, 0),
      totalRequests: keys.reduce((s, k) => s + k.totalRequests, 0),
      totalSpentUsd: keys.reduce((s, k) => s + k.totalSpentUsd, 0),
      totalSavedUsd: keys.reduce((s, k) => s + k.totalSavedUsd, 0),
      keys: keys.map(k => ({
        keyPrefix: k.keyPrefix,
        label: k.label,
        identityTier: k.identityTier,
        balanceUsd: k.balanceUsd,
        freeRequestsRemaining: k.freeRequestsRemaining,
        totalRequests: k.totalRequests,
        totalSpentUsd: k.totalSpentUsd,
        totalSavedUsd: k.totalSavedUsd,
        createdAt: k.createdAt,
        lastUsedAt: k.lastUsedAt,
      })),
    };

    res.json(aggregate);
  } catch (err: any) {
    console.error('[auth] Keys by wallet error:', err.message);
    res.status(500).json({ error: 'Failed to retrieve keys' });
  }
});

// --- Crypto Deposit Info ---

app.get('/api/deposit-address', (_req, res) => {
  res.json({
    address: config.walletAddress,
    network: 'Base',
    chainId: 8453,
    accepts: [
      { token: 'USDC', rate: '1 USDC = $1.00 credit' },
      { token: 'ETH', rate: 'Market rate at time of receipt (CoinGecko)' },
    ],
    note: 'Send USDC or ETH on Base to this address. Your API key must be linked to the sending wallet. Credits appear within 60 seconds.',
  });
});

// --- Stripe Top-Up ---

app.post('/api/topup', async (req, res) => {
  try {
    const apiKey = extractApiKey(req.headers as Record<string, string | string[] | undefined>);
    if (!apiKey) {
      return res.status(401).json({ error: 'Include Authorization: Bearer wf_YOUR_KEY header' });
    }
    const auth = validateApiKey(apiKey);
    if (!auth.authenticated || !auth.keyId) {
      return res.status(401).json({ error: 'Invalid API key' });
    }

    const { amount } = req.body || {};
    const amountCents = parseInt(amount, 10);

    if (!amountCents || !TOP_UP_AMOUNTS.find(a => a.amount === amountCents)) {
      return res.status(400).json({
        error: 'Invalid amount',
        valid_amounts: TOP_UP_AMOUNTS,
        hint: 'Send {"amount": 1000} for $10',
      });
    }

    const baseUrl = `https://${req.headers.host || 'windfall.ecofrontiers.xyz'}`;

    const session = await createCheckoutSession({
      keyId: auth.keyId,
      amountCents,
      successUrl: `${baseUrl}/topup/success?session_id={CHECKOUT_SESSION_ID}`,
      cancelUrl: `${baseUrl}/topup`,
    });

    res.json({ url: session.url, session_id: session.sessionId });
  } catch (err: any) {
    console.error('[topup] Error:', err.message);
    res.status(500).json({ error: 'Failed to create checkout session' });
  }
});

// --- Legal Pages ---

app.get('/terms', (_req, res) => {
  res.sendFile(path.resolve(__dirname, '../public/terms.html'));
});

app.get('/privacy', (_req, res) => {
  res.sendFile(path.resolve(__dirname, '../public/privacy.html'));
});

app.get('/imprint', (_req, res) => {
  res.sendFile(path.resolve(__dirname, '../public/imprint.html'));
});

// --- Top-Up Page (browser) ---

app.get('/topup', (req, res) => {
  res.sendFile(path.resolve(__dirname, '../public/topup.html'));
});

app.get('/topup/success', (req, res) => {
  res.sendFile(path.resolve(__dirname, '../public/topup.html'));
});

// --- Shared Assets (CSS, JS, images, logo) ---

app.use('/assets', express.static(path.resolve(__dirname, '../public/assets')));

// --- robots.txt ---

app.get('/robots.txt', (_req, res) => {
  res.type('text/plain').sendFile(path.resolve(__dirname, '../public/robots.txt'));
});

// --- sitemap.xml ---

app.get('/sitemap.xml', (_req, res) => {
  res.type('application/xml').sendFile(path.resolve(__dirname, '../public/sitemap.xml'));
});

// --- Landing Page (serve static for browser visitors) ---

app.get('/', (_req, res) => {
  const accept = _req.headers.accept || '';
  if (accept.includes('text/html')) {
    return res.sendFile(path.resolve(__dirname, '../public/index.html'));
  }
  res.json({
    service: 'Windfall',
    description: 'Spatially-routed LLM inference for AI agents on Base',
    endpoint: '/v1/chat/completions',
    pricing: `$${config.pricePerRequest}/request (DeepSeek V3), $${config.premiumPricePerRequest}/request (Claude/GPT)`,
    routing: {
      modes: ['cheapest', 'greenest', 'balanced'],
      defaultMode: 'greenest',
    },
    auth: {
      x402: 'Native x402 protocol — any agent with a Base wallet can pay per-request. No API key needed.',
      siwa: 'Sign In With Agent (ERC-8004) — authenticate via wallet signature at POST /api/auth/wallet',
      apiKey: 'Create at POST /api/keys — 25-100 free requests based on onchain identity',
    },
    docs: 'https://windfall.ecofrontiers.xyz',
    status: '/status',
  });
});

// --- Inference Route (with stricter rate limit) ---

app.use('/v1/chat/completions', apiLimiter);
app.use('/', inferenceRouter);

// --- User Dashboard (public — shows per-key stats) ---

app.get('/dashboard', (_req, res) => {
  res.sendFile(path.resolve(__dirname, '../public/dashboard.html'));
});

// --- Admin Command Center (password-protected, moved from /dashboard to /admin) ---

const ADMIN_LOGIN_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow">
  <title>Windfall Admin — Login</title>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #1A1714;
      color: #e0ddd8;
      font-family: 'Manrope', sans-serif;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .login-box {
      background: #23201b;
      border: 1px solid #3a362f;
      border-radius: 12px;
      padding: 2.5rem;
      width: 100%;
      max-width: 380px;
      text-align: center;
    }
    h1 { font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; }
    p { font-size: 0.85rem; color: #9a9590; margin-bottom: 1.5rem; }
    input[type="password"] {
      width: 100%;
      padding: 0.7rem 1rem;
      border: 1px solid #3a362f;
      border-radius: 8px;
      background: #1A1714;
      color: #e0ddd8;
      font-family: 'Manrope', sans-serif;
      font-size: 0.95rem;
      margin-bottom: 1rem;
      outline: none;
    }
    input[type="password"]:focus { border-color: #7c9a6e; }
    button {
      width: 100%;
      padding: 0.7rem;
      border: none;
      border-radius: 8px;
      background: #7c9a6e;
      color: #1A1714;
      font-family: 'Manrope', sans-serif;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover { background: #8fae80; }
    .error { color: #d47b6e; font-size: 0.85rem; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <form class="login-box" method="POST" action="/admin/login">
    <h1>Windfall Admin</h1>
    <p>Enter the admin password to continue.</p>
    <div class="error" id="err" style="display:none"></div>
    <input type="password" name="password" placeholder="Password" autofocus required>
    <button type="submit">Log in</button>
  </form>
</body>
</html>`;

// Admin login endpoint (handles form POST)
app.post('/admin/login', loginLimiter, express.urlencoded({ extended: false }), (req, res) => {
  const password = (req.body as { password?: string })?.password || '';

  // C2: Require password to be set — reject login if not configured
  if (!config.dashboardPassword) {
    return res.status(503).send('Admin panel disabled. Set DASHBOARD_PASSWORD in .env to enable.');
  }

  if (password === config.dashboardPassword) {
    const token = crypto.randomBytes(32).toString('hex');
    dashboardSessions.set(token, Date.now() + SESSION_MAX_AGE_MS);
    res.setHeader('Set-Cookie', `wf_admin_session=${token}; Path=/; HttpOnly; SameSite=Strict; Secure; Max-Age=86400`);
    return res.redirect('/admin');
  }

  res.status(401).send(ADMIN_LOGIN_HTML.replace(
    '<div class="error" id="err" style="display:none"></div>',
    '<div class="error">Incorrect password.</div>'
  ));
});

// Admin auth middleware
app.use('/admin', (req, res, next) => {
  // C2: If no password is configured, disable admin panel entirely
  if (!config.dashboardPassword) {
    return res.status(503).send('Admin panel disabled. Set DASHBOARD_PASSWORD in .env to enable.');
  }

  const cookies = parseCookies(req.headers.cookie);
  const sessionToken = cookies['wf_admin_session'];

  if (isValidSession(sessionToken)) {
    return next();
  }

  // Not authenticated — serve login page
  res.status(401).send(ADMIN_LOGIN_HTML);
});

app.use('/admin', express.static(path.resolve(__dirname, '../dashboard/dist')));

// --- Start Server ---

const server = app.listen(config.port, () => {
  console.log(`
╔══════════════════════════════════════════════╗
║              ⚡ WINDFALL v0.1.0              ║
║   Spatially-Routed Inference Gateway         ║
║   Ecofrontiers SARL                          ║
╠══════════════════════════════════════════════╣
║  Node:     ${config.nodeId.padEnd(33)}║
║  Location: ${config.nodeLocation.padEnd(33)}║
║  Port:     ${String(config.port).padEnd(33)}║
║  Model:    ${config.defaultModel.padEnd(33)}║
║  Price:    $${config.pricePerRequest}/req${' '.repeat(24)}║
║  Wallet:   ${config.walletAddress.slice(0, 10)}...${config.walletAddress.slice(-8)}${' '.repeat(13)}║
║  Stripe:   ${config.stripeSecretKey ? 'configured' : 'not configured'}${' '.repeat(config.stripeSecretKey ? 22 : 18)}║
╚══════════════════════════════════════════════╝
  `);

  // C2: Warn if admin password is not set
  if (!config.dashboardPassword) {
    console.warn('\n⚠️  WARNING: DASHBOARD_PASSWORD is not set. Admin panel (/admin) is DISABLED.');
    console.warn('   Set DASHBOARD_PASSWORD in .env to enable the admin command center.\n');
  }

  // Start energy oracle
  startOracle();

  // Start attestation batcher
  startAttestationBatcher();

  // Start deposit watchers
  startUsdcWatcher();
  startEthWatcher();

  // Start ACP job handler (if enabled)
  startAcpHandler();

  // Purge expired cache entries every 10 minutes
  setInterval(() => {
    const purged = purgeExpired();
    if (purged > 0) console.log(`[cache] Purged ${purged} expired entries`);
  }, 10 * 60 * 1000);

  // Purge contact.jsonl entries older than 12 months — every hour
  setInterval(() => {
    try {
      const contactPath = path.resolve(__dirname, '../data/contact.jsonl');
      if (!fs.existsSync(contactPath)) return;
      const lines = fs.readFileSync(contactPath, 'utf-8').split('\n').filter(l => l.trim());
      const twelveMonthsAgo = Date.now() - 365 * 24 * 60 * 60 * 1000;
      const kept = lines.filter(line => {
        try {
          const entry = JSON.parse(line);
          return new Date(entry.timestamp).getTime() >= twelveMonthsAgo;
        } catch { return true; }
      });
      if (kept.length < lines.length) {
        fs.writeFileSync(contactPath, kept.length > 0 ? kept.join('\n') + '\n' : '');
        console.log(`[retention] Purged ${lines.length - kept.length} contact entries older than 12 months`);
      }
    } catch (err: any) {
      console.error('[retention] Contact purge error:', err.message);
    }
  }, 60 * 60 * 1000);

  // Daily: anonymize wallet addresses in request_log older than 30 days
  setInterval(() => {
    try {
      const anonymized = anonymizeOldRequests();
      if (anonymized > 0) console.log(`[retention] Anonymized ${anonymized} request_log entries older than 30 days`);
    } catch (err: any) {
      console.error('[retention] Anonymize error:', err.message);
    }
  }, 86400000);

  // Daily: delete API keys inactive for 12+ months
  setInterval(() => {
    try {
      const purged = purgeInactiveKeys();
      if (purged > 0) console.log(`[retention] Purged ${purged} API keys inactive for 12+ months`);
    } catch (err: any) {
      console.error('[retention] Key purge error:', err.message);
    }
  }, 86400000);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('[windfall] Shutting down...');
  server.close();
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('[windfall] Shutting down...');
  server.close();
  process.exit(0);
});
