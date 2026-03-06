/**
 * BrainDB Auto-Capture Module
 * 
 * Evaluates tool execution outcomes and encodes noteworthy ones into BrainDB.
 * 
 * Three encoding triggers:
 *   1. FAILURE — Always encode. Error message + what to try instead.
 *   2. NOVEL SUCCESS — First time a tool/pattern succeeds. Encode the workflow.
 *   3. REPEATED SUCCESS — Don't re-encode. Reinforce via Hebbian.
 * 
 * Plugs into the gateway as middleware. OpenClaw plugin sends tool results
 * to POST /memory/capture-execution, this module decides what's worth keeping.
 */

// Pattern signatures we've seen before (in-memory, rebuilt from BrainDB on startup)
const seenPatterns = new Map(); // key: "tool:action_signature" → count

// ─── Classification ──────────────────────────────────────

function classifyOutcome(toolCall) {
  const { tool, args, result, error, durationMs } = toolCall;

  // FAILURE — always interesting
  if (error || (result && typeof result === 'string' && (
    result.includes('command not found') ||
    result.includes('Permission denied') ||
    result.includes('ECONNREFUSED') ||
    result.includes('ENOENT') ||
    result.includes('timeout') ||
    result.includes('404') ||
    result.includes('401') ||
    result.includes('500') ||
    result.includes('Error') ||
    result.includes('not found') ||
    result.includes('No such file')
  ))) {
    return 'failure';
  }

  // Generate a pattern signature
  const sig = generateSignature(tool, args);
  const count = seenPatterns.get(sig) || 0;
  seenPatterns.set(sig, count + 1);

  // NOVEL — first or second time seeing this pattern
  if (count < 2) return 'novel';

  // REPEATED — reinforce, don't re-encode
  return 'repeated';
}

function generateSignature(tool, args) {
  // Create a stable signature that groups similar tool calls
  switch (tool) {
    case 'exec':
      // Group by command prefix (first word)
      const cmd = (args?.command || '').split(/\s+/)[0];
      return `exec:${cmd}`;
    case 'web_fetch':
      // Group by domain
      try {
        const domain = new URL(args?.url || '').hostname;
        return `web_fetch:${domain}`;
      } catch { return 'web_fetch:unknown'; }
    case 'web_search':
      return 'web_search:query';
    case 'message':
      return `message:${args?.action || 'send'}:${args?.channel || 'default'}`;
    case 'nodes':
      return `nodes:${args?.action || 'run'}:${args?.node || 'any'}`;
    case 'cron':
      return `cron:${args?.action || 'add'}`;
    case 'browser':
      return `browser:${args?.action || 'navigate'}`;
    case 'read':
    case 'write':
    case 'edit':
      // Group by file extension
      const ext = (args?.path || args?.file_path || '').split('.').pop() || 'unknown';
      return `${tool}:.${ext}`;
    default:
      return `${tool}:default`;
  }
}

// ─── Memory Generation ──────────────────────────────────

function generateFailureMemory(toolCall) {
  const { tool, args, result, error, durationMs } = toolCall;
  const errorMsg = error || extractError(result);

  // Try to suggest an alternative
  const alternative = suggestAlternative(tool, args, errorMsg);

  let content = `Tool "${tool}" failed`;
  if (args?.command) content += ` running "${truncate(args.command, 80)}"`;
  if (args?.url) content += ` fetching "${truncate(args.url, 80)}"`;
  if (args?.node) content += ` on node "${args.node}"`;
  content += `. Error: ${truncate(errorMsg, 150)}.`;
  if (alternative) content += ` ${alternative}`;

  return {
    event: `Failure: ${tool} — ${truncate(errorMsg, 60)}`,
    content,
    shard: 'procedural',
    context: { category: 'failure-memory', source: 'auto-capture', tool, timestamp: new Date().toISOString() },
    motivationDelta: { protect: 0.5, serve: 0.3 },
    dedupThreshold: 0.85,
  };
}

function generateNovelMemory(toolCall) {
  const { tool, args, result, durationMs } = toolCall;

  let content = `Tool "${tool}" succeeded`;
  if (args?.command) content += ` running "${truncate(args.command, 100)}"`;
  if (args?.url) content += ` fetching "${truncate(args.url, 80)}"`;
  if (args?.action) content += ` with action="${args.action}"`;
  if (args?.node) content += ` on node "${args.node}"`;
  if (durationMs) content += ` in ${durationMs}ms`;
  content += '.';

  // Add result summary for useful context
  if (result && typeof result === 'string' && result.length > 0) {
    const summary = truncate(result, 100);
    if (summary.length > 20) content += ` Result preview: ${summary}`;
  }

  return {
    event: `Pattern: ${tool}${args?.action ? ':' + args.action : ''}${args?.command ? ' — ' + truncate(args.command.split(/\s+/)[0], 30) : ''}`,
    content,
    shard: 'procedural',
    context: { category: 'execution-pattern', source: 'auto-capture', tool, timestamp: new Date().toISOString() },
    motivationDelta: { serve: 0.3, grow: 0.2 },
    dedupThreshold: 0.85,
  };
}

// ─── Helpers ─────────────────────────────────────────────

function extractError(result) {
  if (!result || typeof result !== 'string') return 'unknown error';
  // Find the most informative error line
  const lines = result.split('\n').filter(l => l.trim());
  const errorLine = lines.find(l =>
    /error|fail|denied|refused|timeout|not found|command not found/i.test(l)
  );
  return errorLine || lines[lines.length - 1] || 'unknown error';
}

function suggestAlternative(tool, args, error) {
  // Common failure → alternative mappings
  if (tool === 'exec' && /permission denied.*publickey/i.test(error)) {
    return 'Use nodes(action="run") instead of SSH for remote commands.';
  }
  if (tool === 'exec' && /command not found/i.test(error)) {
    const cmd = (args?.command || '').split(/\s+/)[0];
    return `The "${cmd}" command is not installed in this environment.`;
  }
  if (tool === 'web_fetch' && /empty|no content/i.test(error)) {
    return 'This site may require JavaScript. Try the browser tool instead.';
  }
  if (tool === 'exec' && /timeout/i.test(error)) {
    return 'Command timed out. Try increasing timeout or running in background with yieldMs.';
  }
  if (/ECONNREFUSED/i.test(error)) {
    return 'Service is not running or wrong port. Check if the service needs to be started.';
  }
  return null;
}

function truncate(str, max) {
  if (!str) return '';
  return str.length > max ? str.slice(0, max) + '...' : str;
}

// ─── Express Route Handler ──────────────────────────────

function createCaptureRoute(encodeFn, recallFn) {
  return async (req, res) => {
    const start = Date.now();
    try {
      const toolCall = req.body;
      const { tool, args, result, error, durationMs } = toolCall;

      if (!tool) {
        return res.status(400).json({ ok: false, error: 'tool field required' });
      }

      // Skip noisy/low-value tool calls
      if (['read', 'session_status'].includes(tool) && !error) {
        return res.json({ ok: true, action: 'skipped', reason: 'low-value-success', latency: Date.now() - start });
      }

      const classification = classifyOutcome(toolCall);

      if (classification === 'repeated') {
        // Hebbian reinforcement — find and strengthen existing pattern
        const sig = generateSignature(tool, args);
        try {
          const existing = await recallFn({ query: `${tool} ${args?.action || ''} ${args?.command?.split(/\s+/)[0] || ''}`.trim(), maxResults: 1, shards: ['procedural'] });
          if (existing.length > 0 && existing[0].similarity > 0.6) {
            // Memory exists and is relevant — Hebbian will handle reinforcement via normal recall
            return res.json({
              ok: true, action: 'reinforced', pattern: sig,
              count: seenPatterns.get(sig) || 0, latency: Date.now() - start,
            });
          }
        } catch {}
        return res.json({ ok: true, action: 'skipped', reason: 'repeated', pattern: sig, latency: Date.now() - start });
      }

      // Generate and encode memory
      const memory = classification === 'failure'
        ? generateFailureMemory(toolCall)
        : generateNovelMemory(toolCall);

      const encodeResult = await encodeFn(memory);

      res.json({
        ok: true,
        action: classification === 'failure' ? 'encoded-failure' : 'encoded-novel',
        encoded: encodeResult?.ok || false,
        deduplicated: encodeResult?.deduplicated || false,
        memory: { event: memory.event, category: memory.context.category },
        latency: Date.now() - start,
      });
    } catch (e) {
      res.status(500).json({ ok: false, error: e.message, latency: Date.now() - start });
    }
  };
}

// ─── Warm Pattern Cache from BrainDB ────────────────────

async function warmPatternCache(recallFn) {
  try {
    const results = await recallFn({
      query: 'tool execution pattern workflow',
      maxResults: 50,
      shards: ['procedural'],
    });
    let warmed = 0;
    for (const r of results) {
      if (r.context?.source === 'auto-capture' || r.context?.source === 'execution-awareness') {
        const tool = r.context?.tool || r.trigger?.split(':')[0]?.replace('Pattern: ', '') || '';
        if (tool) {
          const sig = `${tool}:warmed`;
          seenPatterns.set(sig, (seenPatterns.get(sig) || 0) + 3); // Pre-count so we don't re-encode known patterns
          warmed++;
        }
      }
    }
    console.log(`🧠 Auto-capture: warmed ${warmed} known patterns from BrainDB`);
  } catch (e) {
    console.warn('Auto-capture: failed to warm pattern cache:', e.message);
  }
}

export { createCaptureRoute, warmPatternCache, classifyOutcome, seenPatterns };
