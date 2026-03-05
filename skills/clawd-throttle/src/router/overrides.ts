import type { OverrideResult } from './types.js';
import type { LogReader } from '../logging/reader.js';
import { createLogger } from '../utils/logger.js';

const log = createLogger('overrides');

// Model hierarchy for sub-agent step-down (cheapest → most expensive)
const MODEL_HIERARCHY: string[] = [
  'gemini-2.5-flash',                // tier 0 — budget
  'grok-4-1-fast-non-reasoning',     // tier 1 — speed
  'claude-haiku-4-5',                // tier 2 — capable
  'claude-sonnet-4-5',               // tier 3 — balanced
  'claude-opus-4-6',                 // tier 4 — premium
];

// Default cheapest model for heartbeats
const HEARTBEAT_MODEL = 'grok-4-1-fast-non-reasoning';

// Force model aliases: short name → catalog model ID
export const FORCE_MODEL_MAP: Record<string, string> = {
  // Anthropic
  opus: 'claude-opus-4-6',
  'opus-4-6': 'claude-opus-4-6',
  'opus-4-5': 'claude-opus-4-5',
  sonnet: 'claude-sonnet-4-5',
  haiku: 'claude-haiku-4-5',
  'haiku-3-5': 'claude-haiku-3-5',
  flash: 'gemini-2.5-flash',
  // OpenAI
  'gpt-5': 'gpt-5.2',
  'gpt-5.2': 'gpt-5.2',
  'gpt-5.1': 'gpt-5.1',
  'gpt-5-mini': 'gpt-5-mini',
  'gpt-5-nano': 'gpt-5-nano',
  'gpt-4o': 'gpt-4o',
  'gpt-4o-mini': 'gpt-4o-mini',
  o3: 'o3',
  // DeepSeek
  deepseek: 'deepseek-chat',
  'deepseek-r1': 'deepseek-reasoner',
  'deepseek-reasoner': 'deepseek-reasoner',
  // xAI / Grok
  grok: 'grok-4-0709',
  'grok-4': 'grok-4-0709',
  'grok-4-0709': 'grok-4-0709',
  'grok-3': 'grok-3',
  'grok-mini': 'grok-3-mini',
  'grok-fast': 'grok-4-1-fast-non-reasoning',
  'grok-4.1-fast': 'grok-4-1-fast-non-reasoning',
  'grok-4-1-fast-non-reasoning': 'grok-4-1-fast-non-reasoning',
  // Moonshot / Kimi
  kimi: 'kimi-k2.5',
  'kimi-thinking': 'kimi-k2-thinking',
  // Mistral
  mistral: 'mistral-large',
  'mistral-small': 'mistral-small',
  codestral: 'codestral',
  // Ollama
  local: 'ollama-default',
  ollama: 'ollama-default',
};

// Legacy override kinds for backward compatibility
const LEGACY_FORCE_KINDS: Record<string, OverrideResult['kind']> = {
  opus: 'force_opus',
  sonnet: 'force_sonnet',
  flash: 'force_flash',
};

export function detectOverrides(
  messages: Array<{ role: string; content: string }>,
  forceModel: string | undefined,
  parentRequestId: string | undefined,
  logReader: LogReader,
): OverrideResult {
  const lastUserContent = messages
    .filter(m => m.role === 'user')
    .pop()?.content ?? '';

  // 1. Heartbeat / summary detection
  if (isHeartbeatOrSummary(lastUserContent)) {
    log.debug('Override: heartbeat/summary detected');
    return {
      kind: 'heartbeat',
      forcedModelId: HEARTBEAT_MODEL,
    };
  }

  // 2. Explicit force commands (via forceModel parameter)
  if (forceModel && FORCE_MODEL_MAP[forceModel]) {
    const kind = LEGACY_FORCE_KINDS[forceModel] ?? 'force_model';
    return { kind, forcedModelId: FORCE_MODEL_MAP[forceModel] };
  }

  // 3. Slash-command force (e.g. /opus, /grok, /deepseek)
  const trimmed = lastUserContent.trim().toLowerCase();
  if (trimmed.startsWith('/')) {
    const command = trimmed.split(/\s/)[0]!.slice(1); // strip leading /
    if (FORCE_MODEL_MAP[command]) {
      const kind = LEGACY_FORCE_KINDS[command] ?? 'force_model';
      log.debug(`Override: slash command /${command} => ${FORCE_MODEL_MAP[command]}`);
      return { kind, forcedModelId: FORCE_MODEL_MAP[command] };
    }
  }

  // 4. Sub-agent tier inheritance
  if (parentRequestId) {
    const parentEntry = logReader.getEntryById(parentRequestId);
    if (parentEntry) {
      const steppedDown = stepDownModel(parentEntry.selectedModel);
      const inherited = steppedDown === parentEntry.selectedModel;
      log.debug(
        `Sub-agent: parent=${parentEntry.selectedModel}, child=${steppedDown}, ` +
        `action=${inherited ? 'inherit' : 'stepdown'}`
      );
      return {
        kind: inherited ? 'sub_agent_inherit' : 'sub_agent_stepdown',
        forcedModelId: steppedDown,
      };
    } else {
      log.warn(`Sub-agent parentRequestId=${parentRequestId} not found in log`);
    }
  }

  // 5. No override
  return { kind: 'none' };
}

function isHeartbeatOrSummary(text: string): boolean {
  const normalized = text.trim().toLowerCase();

  const patterns: RegExp[] = [
    /^(ping|pong|heartbeat|health[- ]?check|status[- ]?check|alive\??|are you there\??)$/,
    /^(summarize|summary|tldr|tl;dr|recap|brief overview)$/,
    /^(summarize|summary|tldr|tl;dr|recap|brief overview)\s+(this|the|our|above|conversation|chat|thread|discussion|everything)$/,
    /^give\s+me\s+a\s+(brief\s+)?(summary|recap|overview)$/,
    /^can\s+you\s+(summarize|recap)\s+(this|the|our|everything)(\??)$/,
  ];

  return patterns.some(p => p.test(normalized));
}

function stepDownModel(parentModelId: string): string {
  const parentIndex = MODEL_HIERARCHY.indexOf(parentModelId);

  if (parentIndex === -1) {
    log.warn(`Unknown model in hierarchy: ${parentModelId}`);
    return parentModelId;
  }

  if (parentIndex === 0) {
    return parentModelId;
  }

  return MODEL_HIERARCHY[parentIndex - 1]!;
}
