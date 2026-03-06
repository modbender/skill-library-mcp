#!/usr/bin/env node
/**
 * iblai-router — Local cost-optimizing proxy for Anthropic Claude models.
 *
 * Sits between OpenClaw and the Anthropic API, automatically routing each
 * request to the cheapest capable Claude model using weighted scoring.
 *
 * All scoring config lives in config.json (or ROUTER_CONFIG env path).
 * Zero dependencies — just Node.js standard library.
 *
 * Usage:
 *   ANTHROPIC_API_KEY=sk-ant-... node server.js
 */

const http = require("http");
const https = require("https");
const fs = require("fs");
const path = require("path");

// ─── Load Config ───

const CONFIG_PATH = process.env.ROUTER_CONFIG || path.join(__dirname, "config.json");

function loadConfig() {
  const raw = fs.readFileSync(CONFIG_PATH, "utf-8");
  const cfg = JSON.parse(raw);

  // Compile multiStepPatterns from strings to RegExp
  if (cfg.scoring.multiStepPatterns) {
    cfg.scoring.multiStepPatterns = cfg.scoring.multiStepPatterns.map(p =>
      p instanceof RegExp ? p : new RegExp(p, "i")
    );
  }

  return cfg;
}

let config = loadConfig();

// Watch for config changes (hot reload)
fs.watchFile(CONFIG_PATH, { interval: 2000 }, () => {
  try {
    config = loadConfig();
    console.log("[router] Config reloaded from", CONFIG_PATH);
  } catch (e) {
    console.error("[router] Config reload failed:", e.message);
  }
});

// ─── Environment ───

const PORT = parseInt(process.env.ROUTER_PORT || "8402", 10);
const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;
const LOG_ROUTING = process.env.ROUTER_LOG !== "0";

// ─── Dimension Scorers ───

function scoreTokenCount(tokens, thresholds) {
  if (tokens < thresholds.simple) return { score: -0.8, signal: `short(${tokens}t)` };
  if (tokens > thresholds.complex) return { score: 0.8, signal: `long(${tokens}t)` };
  return { score: 0, signal: null };
}

function scoreKeywords(text, keywords, threshLow, threshHigh, scoreLow, scoreHigh) {
  const matches = keywords.filter(kw => text.includes(kw.toLowerCase()));
  if (matches.length >= threshHigh) return { score: scoreHigh, signal: matches.slice(0, 3).join(",") };
  if (matches.length >= threshLow) return { score: scoreLow, signal: matches.slice(0, 2).join(",") };
  return { score: 0, signal: null };
}

function scorePatterns(text, patterns) {
  const hits = patterns.filter(p => p.test(text));
  if (hits.length > 0) return { score: 0.5, signal: "multi-step" };
  return { score: 0, signal: null };
}

function scoreQuestions(text) {
  const count = (text.match(/\?/g) || []).length;
  if (count > 3) return { score: 0.5, signal: `${count}q` };
  return { score: 0, signal: null };
}

// ─── Main Classifier ───

function classify(text, estimatedTokens) {
  const s = config.scoring;
  const lower = text.toLowerCase();

  const dims = {
    tokenCount:       scoreTokenCount(estimatedTokens, s.tokenThresholds),
    codePresence:     scoreKeywords(lower, s.codeKeywords, 1, 3, 0.5, 1.0),
    reasoningMarkers: scoreKeywords(lower, s.reasoningKeywords, 1, 2, 0.6, 1.0),
    technicalTerms:   scoreKeywords(lower, s.technicalKeywords, 2, 4, 0.5, 1.0),
    creativeMarkers:  scoreKeywords(lower, s.creativeKeywords, 1, 2, 0.4, 0.7),
    simpleIndicators: scoreKeywords(lower, s.simpleKeywords, 1, 2, -0.8, -1.0),
    multiStep:        scorePatterns(lower, s.multiStepPatterns),
    questionCount:    scoreQuestions(text),
    imperativeVerbs:  scoreKeywords(lower, s.imperativeVerbs, 1, 2, 0.3, 0.5),
    constraints:      scoreKeywords(lower, s.constraintKeywords, 1, 3, 0.3, 0.7),
    outputFormat:     scoreKeywords(lower, s.formatKeywords, 1, 2, 0.4, 0.7),
    domainSpecific:   scoreKeywords(lower, s.domainKeywords, 1, 2, 0.5, 0.8),
    agenticTask:      scoreKeywords(lower, s.agenticKeywords, 2, 4, 0.4, 0.8),
    relayIndicators:  scoreKeywords(lower, s.relayKeywords, 1, 2, -0.9, -1.0),
  };

  // Weighted score
  let score = 0;
  const signals = [];
  for (const [name, dim] of Object.entries(dims)) {
    const w = s.weights[name] || 0;
    score += dim.score * w;
    if (dim.signal) signals.push(`${name}:${dim.signal}`);
  }

  const models = config.models;
  const overrides = s.overrides || {};

  // Override: 2+ reasoning keywords → HEAVY
  const reasoningMin = overrides.reasoningKeywordMin || 2;
  const reasoningHits = s.reasoningKeywords.filter(kw => lower.includes(kw.toLowerCase()));
  if (reasoningHits.length >= reasoningMin) {
    return { model: models.HEAVY, tier: "HEAVY", score, confidence: 0.95, signals, reasoning: "reasoning-override" };
  }

  // Override: large context → HEAVY
  const largeCtx = overrides.largeContextTokens || 50000;
  if (estimatedTokens > largeCtx) {
    return { model: models.HEAVY, tier: "HEAVY", score, confidence: 0.95, signals, reasoning: "large-context" };
  }

  // Map score to tier
  const { lightMedium, mediumHeavy } = s.boundaries;
  let tier, distFromBoundary;

  if (score < lightMedium) {
    tier = "LIGHT";
    distFromBoundary = lightMedium - score;
  } else if (score < mediumHeavy) {
    tier = "MEDIUM";
    distFromBoundary = Math.min(score - lightMedium, mediumHeavy - score);
  } else {
    tier = "HEAVY";
    distFromBoundary = score - mediumHeavy;
  }

  // Sigmoid confidence
  const confidence = 1 / (1 + Math.exp(-s.confidenceSteepness * distFromBoundary));

  // Ambiguous → default MEDIUM
  if (confidence < s.confidenceThreshold) {
    return { model: models.MEDIUM, tier: "MEDIUM", score, confidence, signals, reasoning: "ambiguous→medium" };
  }

  const model = tier === "LIGHT" ? models.LIGHT : tier === "HEAVY" ? models.HEAVY : models.MEDIUM;
  return { model, tier, score, confidence, signals, reasoning: "scored" };
}

// ─── Extract scoring text from Anthropic messages format ───

function extractText(body) {
  let text = "";
  // Skip system prompt — it's the same for every request (OpenClaw's large
  // system prompt) and inflates every score to HEAVY. Score only user messages.
  if (Array.isArray(body.messages)) {
    const recent = body.messages.slice(-3);
    for (const msg of recent) {
      if (typeof msg.content === "string") text += msg.content + " ";
      else if (Array.isArray(msg.content)) {
        for (const block of msg.content) {
          if (block.type === "text") text += block.text + " ";
        }
      }
    }
  }
  return text;
}

// ─── Proxy to Anthropic ───

function proxyToAnthropic(req, res, body, routedModel, tier) {
  body.model = routedModel;

  // Haiku doesn't support thinking — strip it when routing to LIGHT tier
  if (tier === "LIGHT") {
    delete body.thinking;
    // Also strip thinking budget from anthropic-beta header
    if (req.headers["anthropic-beta"]) {
      const betas = req.headers["anthropic-beta"].split(",").map(s => s.trim())
        .filter(b => !b.startsWith("thinking") && !b.startsWith("extended-thinking"));
      if (betas.length > 0) {
        req.headers["anthropic-beta"] = betas.join(",");
      } else {
        delete req.headers["anthropic-beta"];
      }
    }
  }
  const payload = JSON.stringify(body);

  // Support custom API base URL from config (e.g. OpenRouter)
  const baseUrl = config.apiBaseUrl || "https://api.anthropic.com";
  const parsed = new URL(baseUrl);

  const options = {
    hostname: parsed.hostname,
    port: parsed.port || (parsed.protocol === "https:" ? 443 : 80),
    path: (parsed.pathname.replace(/\/$/, "") || "") + "/v1/messages",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Content-Length": Buffer.byteLength(payload),
    },
  };

  // Use appropriate auth header based on target
  const isOpenRouter = parsed.hostname.includes("openrouter");
  if (isOpenRouter) {
    options.headers["Authorization"] = `Bearer ${ANTHROPIC_API_KEY}`;
    options.headers["HTTP-Referer"] = config.openRouterReferer || "https://github.com/iblai/iblai-openclaw-router";
  } else {
    options.headers["x-api-key"] = ANTHROPIC_API_KEY;
    options.headers["anthropic-version"] = req.headers["anthropic-version"] || "2023-06-01";
    if (req.headers["anthropic-beta"]) {
      options.headers["anthropic-beta"] = req.headers["anthropic-beta"];
    }
  }

  const transport = parsed.protocol === "https:" ? https : http;
  const upstream = transport.request(options, (upstreamRes) => {
    res.writeHead(upstreamRes.statusCode, upstreamRes.headers);
    upstreamRes.pipe(res);
  });

  upstream.on("error", (err) => {
    console.error("[router] upstream error:", err.message);
    if (!res.headersSent) {
      res.writeHead(502, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: { type: "proxy_error", message: err.message } }));
    }
  });

  upstream.write(payload);
  upstream.end();
}

// ─── Stats ───

const stats = {
  total: 0,
  byTier: {},
  estimatedCost: 0,
  baselineCost: 0,
  startedAt: new Date().toISOString(),
};

// ─── HTTP Server ───

const server = http.createServer((req, res) => {
  if (req.method === "GET" && (req.url === "/health" || req.url === "/")) {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", models: config.models, port: PORT }));
    return;
  }

  if (req.method === "GET" && req.url === "/stats") {
    const savings = stats.baselineCost > 0
      ? ((1 - stats.estimatedCost / stats.baselineCost) * 100).toFixed(1) + "%"
      : "n/a";
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ...stats, savings }));
    return;
  }

  if (req.method !== "POST" || !req.url.startsWith("/v1/messages")) {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Not found. Use POST /v1/messages" }));
    return;
  }

  let chunks = [];
  req.on("data", (chunk) => chunks.push(chunk));
  req.on("end", () => {
    let body;
    try {
      body = JSON.parse(Buffer.concat(chunks).toString());
    } catch (e) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Invalid JSON" }));
      return;
    }

    const text = extractText(body);
    const estimatedTokens = Math.ceil(text.length / 4);
    const decision = classify(text, estimatedTokens);

    // Track stats
    stats.total++;
    stats.byTier[decision.tier] = (stats.byTier[decision.tier] || 0) + 1;
    const cost = config.costs[decision.model] || { input: 0 };
    stats.estimatedCost += (estimatedTokens / 1_000_000) * cost.input;
    const opusCost = (estimatedTokens / 1_000_000) * (config.costs[config.models.HEAVY]?.input || 15);
    stats.baselineCost += opusCost;

    if (LOG_ROUTING) {
      const savings = opusCost > 0
        ? ((opusCost - (estimatedTokens / 1_000_000) * cost.input) / opusCost * 100).toFixed(0)
        : 0;
      console.log(
        `[router] ${decision.tier.padEnd(6)} → ${decision.model} ` +
        `| score=${decision.score.toFixed(3)} conf=${decision.confidence.toFixed(2)} ` +
        `| ${decision.reasoning} | -${savings}% | ${text.slice(0, 80).replace(/\n/g, " ")}...`
      );
    }

    proxyToAnthropic(req, res, body, decision.model, decision.tier);
  });
});

// ─── Start ───

if (!ANTHROPIC_API_KEY) {
  console.error("[router] ANTHROPIC_API_KEY not set. Exiting.");
  process.exit(1);
}

server.listen(PORT, "127.0.0.1", () => {
  console.log(`[router] iblai-router listening on http://127.0.0.1:${PORT}`);
  console.log(`[router] Config: ${CONFIG_PATH}`);
  console.log(`[router] Models: LIGHT=${config.models.LIGHT} MEDIUM=${config.models.MEDIUM} HEAVY=${config.models.HEAVY}`);
});
