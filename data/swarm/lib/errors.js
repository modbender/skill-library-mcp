/**
 * Swarm Error Diagnostics
 * 
 * Structured error handling with actionable suggestions.
 * Every error tells you: what happened, where, why, and how to fix it.
 */

/**
 * Classify an error and return structured diagnostics
 */
function diagnoseError(error, context = {}) {
  const msg = error?.message || String(error);
  const diag = {
    error: msg,
    category: 'unknown',
    stage: context.stage || null,
    task: context.task || null,
    suggestion: null,
    retryable: false,
    severity: 'error', // error, warning, fatal
  };

  // Rate limiting
  if (/rate.?limit|429|too many requests|quota/i.test(msg)) {
    diag.category = 'rate_limit';
    diag.suggestion = 'Reduce max_concurrent_api in config, or wait and retry. Check Gemini API quotas.';
    diag.retryable = true;
    diag.severity = 'warning';
    return diag;
  }

  // Authentication
  if (/401|403|unauthorized|forbidden|invalid.*key|api.?key/i.test(msg)) {
    diag.category = 'auth';
    diag.suggestion = 'Check your API key. Run: security find-generic-password -a oaiken -s "gemini/api-key" -w';
    diag.retryable = false;
    diag.severity = 'fatal';
    return diag;
  }

  // Timeout
  if (/timeout|timed.?out|ETIMEDOUT|ESOCKETTIMEDOUT/i.test(msg)) {
    diag.category = 'timeout';
    diag.suggestion = context.stage 
      ? `Stage "${context.stage}" timed out. Try: increase stageTimeoutMs, reduce input size, or use "quick" depth.`
      : 'Task timed out. Increase timeout_ms in config or simplify the prompt.';
    diag.retryable = true;
    return diag;
  }

  // Network
  if (/ECONNREFUSED|ENOTFOUND|ENETUNREACH|fetch failed|network/i.test(msg)) {
    diag.category = 'network';
    diag.suggestion = 'Network error. Check internet connection and that the Gemini API is reachable.';
    diag.retryable = true;
    return diag;
  }

  // Model errors
  if (/model.*not found|invalid.*model|unsupported/i.test(msg)) {
    diag.category = 'model';
    diag.suggestion = `Model not available. Check config provider.model. Available: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash.`;
    diag.retryable = false;
    return diag;
  }

  // Content safety
  if (/safety|blocked|harmful|prohibited|content.?filter|cannot help|can't help|refuse|I'm not able/i.test(msg)) {
    diag.category = 'safety';
    diag.suggestion = 'Content was blocked by safety filters. Rephrase the prompt to avoid triggering content filters.';
    diag.retryable = false;
    return diag;
  }

  // Input too large
  if (/too.?large|too.?long|token.?limit|context.?length|max.*token/i.test(msg)) {
    diag.category = 'input_size';
    diag.suggestion = 'Input exceeds model context window. Reduce input size or use chain with smaller chunks.';
    diag.retryable = false;
    return diag;
  }

  // Quality validation failure
  if (/quality.?check|empty.*response|degenerate|refusal|truncated/i.test(msg)) {
    diag.category = 'quality';
    diag.suggestion = 'Output failed quality check. Will retry automatically. If persistent, simplify the prompt.';
    diag.retryable = true;
    diag.severity = 'warning';
    return diag;
  }

  // JSON parse errors (bad response from API)
  if (/JSON|parse|unexpected.?token|SyntaxError/i.test(msg)) {
    diag.category = 'parse';
    diag.suggestion = 'API returned malformed response. Usually transient — retry should work.';
    diag.retryable = true;
    return diag;
  }

  // Catch-all
  diag.suggestion = 'Unexpected error. Check daemon logs: swarm logs 50';
  diag.retryable = true;
  return diag;
}

/**
 * Format error for NDJSON streaming response
 */
function formatErrorEvent(error, context = {}) {
  const diag = diagnoseError(error, context);
  return {
    event: 'error',
    ...diag,
    timestamp: Date.now(),
  };
}

/**
 * Format error for CLI display
 */
function formatErrorCLI(error, context = {}) {
  const diag = diagnoseError(error, context);
  const icon = diag.severity === 'fatal' ? '💀' : diag.severity === 'warning' ? '⚠️' : '❌';
  
  let output = `${icon} ${diag.category.toUpperCase()}: ${diag.error}`;
  if (diag.stage) output += `\n   Stage: ${diag.stage}`;
  if (diag.suggestion) output += `\n   Fix: ${diag.suggestion}`;
  if (diag.retryable) output += `\n   (retryable)`;
  
  return output;
}

module.exports = { diagnoseError, formatErrorEvent, formatErrorCLI };
