// Hub Search-First Evolution: query evomap-hub for reusable solutions before local solve.
//
// Flow: extractSignals() -> hubSearch(signals) -> if hit: reuse; if miss: normal evolve
// Two modes: direct (skip local reasoning) | reference (inject into prompt as strong hint)
//
// Uses POST /a2a/fetch with signals field (protocol-native) instead of GET /a2a/assets/search.
// This returns full payload (content, diff, strategy) in a single round-trip.

const { getNodeId, buildFetch } = require('./a2aProtocol');
const { logAssetCall } = require('./assetCallLog');

const DEFAULT_MIN_REUSE_SCORE = 0.72;
const DEFAULT_REUSE_MODE = 'reference'; // 'direct' | 'reference'
const MAX_STREAK_CAP = 5;
const TIMEOUT_REASON = 'hub_search_timeout';

function getHubUrl() {
  return (process.env.A2A_HUB_URL || '').replace(/\/+$/, '');
}

function getReuseMode() {
  const m = String(process.env.EVOLVER_REUSE_MODE || DEFAULT_REUSE_MODE).toLowerCase();
  return m === 'direct' ? 'direct' : 'reference';
}

function getMinReuseScore() {
  const n = Number(process.env.EVOLVER_MIN_REUSE_SCORE);
  return Number.isFinite(n) && n > 0 ? n : DEFAULT_MIN_REUSE_SCORE;
}

/**
 * Score a hub asset for local reuse quality.
 * rank = confidence * min(max(success_streak, 1), MAX_STREAK_CAP) * (reputation / 100)
 * Streak is capped to prevent unbounded score inflation.
 */
function scoreHubResult(asset) {
  const confidence = Number(asset.confidence) || 0;
  const streak = Math.min(Math.max(Number(asset.success_streak) || 0, 1), MAX_STREAK_CAP);
  const repRaw = Number(asset.reputation_score);
  const reputation = Number.isFinite(repRaw) ? repRaw : 50;
  return confidence * streak * (reputation / 100);
}

/**
 * Pick the best matching asset above the threshold.
 * Returns { match, score, mode } or null if nothing qualifies.
 */
function pickBestMatch(results, threshold) {
  if (!Array.isArray(results) || results.length === 0) return null;

  let best = null;
  let bestScore = 0;

  for (const asset of results) {
    if (asset.status && asset.status !== 'promoted') continue;
    const s = scoreHubResult(asset);
    if (s > bestScore) {
      bestScore = s;
      best = asset;
    }
  }

  if (!best || bestScore < threshold) return null;

  return {
    match: best,
    score: Math.round(bestScore * 1000) / 1000,
    mode: getReuseMode(),
  };
}

/**
 * Search the hub for reusable assets matching the given signals.
 * Uses POST /a2a/fetch with signals (protocol-native, returns full payload).
 * Falls back to GET /a2a/assets/search if fetch fails.
 * Returns { hit: true, match, score, mode } or { hit: false }.
 */
async function hubSearch(signals, opts) {
  const hubUrl = getHubUrl();
  if (!hubUrl) return { hit: false, reason: 'no_hub_url' };

  const signalList = Array.isArray(signals)
    ? signals.map(s => typeof s === 'string' ? s.trim() : '').filter(Boolean)
    : [];
  if (signalList.length === 0) return { hit: false, reason: 'no_signals' };

  const threshold = (opts && Number.isFinite(opts.threshold)) ? opts.threshold : getMinReuseScore();
  const timeout = (opts && Number.isFinite(opts.timeoutMs)) ? opts.timeoutMs : 8000;

  try {
    const fetchMsg = buildFetch({ signals: signalList });
    const endpoint = hubUrl + '/a2a/fetch';

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(TIMEOUT_REASON), timeout);

    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    const token = process.env.A2A_HUB_TOKEN;
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(endpoint, {
      method: 'POST',
      headers,
      body: JSON.stringify(fetchMsg),
      signal: controller.signal,
    });
    clearTimeout(timer);

    if (!res.ok) {
      logAssetCall({
        run_id: (opts && opts.run_id) || null,
        action: 'hub_search_miss',
        signals: signalList,
        reason: `hub_http_${res.status}`,
        via: 'fetch_with_signals',
      });
      return { hit: false, reason: `hub_http_${res.status}` };
    }

    const data = await res.json();
    const results = (data && data.payload && Array.isArray(data.payload.results))
      ? data.payload.results
      : [];

    if (results.length === 0) {
      logAssetCall({
        run_id: (opts && opts.run_id) || null,
        action: 'hub_search_miss',
        signals: signalList,
        reason: 'no_results',
        via: 'fetch_with_signals',
      });
      return { hit: false, reason: 'no_results' };
    }

    const pick = pickBestMatch(results, threshold);
    if (!pick) {
      logAssetCall({
        run_id: (opts && opts.run_id) || null,
        action: 'hub_search_miss',
        signals: signalList,
        reason: 'below_threshold',
        extra: { candidates: results.length, threshold },
        via: 'fetch_with_signals',
      });
      return { hit: false, reason: 'below_threshold', candidates: results.length };
    }

    console.log(`[HubSearch] Hit via fetch+signals: ${pick.match.asset_id || 'unknown'} (score=${pick.score}, mode=${pick.mode})`);

    logAssetCall({
      run_id: (opts && opts.run_id) || null,
      action: 'hub_search_hit',
      asset_id: pick.match.asset_id || null,
      asset_type: pick.match.asset_type || pick.match.type || null,
      source_node_id: pick.match.source_node_id || null,
      chain_id: pick.match.chain_id || null,
      score: pick.score,
      mode: pick.mode,
      signals: signalList,
      via: 'fetch_with_signals',
    });

    return {
      hit: true,
      match: pick.match,
      score: pick.score,
      mode: pick.mode,
      asset_id: pick.match.asset_id || null,
      source_node_id: pick.match.source_node_id || null,
      chain_id: pick.match.chain_id || null,
    };
  } catch (err) {
    const isTimeout = err.name === 'AbortError' || (err.cause && err.cause === TIMEOUT_REASON);
    const reason = isTimeout ? 'timeout' : 'fetch_error';
    console.log(`[HubSearch] Failed (non-fatal, ${reason}): ${err.message}`);
    logAssetCall({
      run_id: (opts && opts.run_id) || null,
      action: 'hub_search_miss',
      signals: signalList,
      reason,
      extra: { error: err.message },
      via: 'fetch_with_signals',
    });
    return { hit: false, reason, error: err.message };
  }
}

module.exports = {
  hubSearch,
  scoreHubResult,
  pickBestMatch,
  getReuseMode,
  getMinReuseScore,
  getHubUrl,
};
