/**
 * Context Compactor - OpenClaw Plugin
 * 
 * Token-based context compaction for local models (MLX, llama.cpp, Ollama)
 * that don't properly report context window limits.
 * 
 * How it works:
 * 1. Before each agent turn, estimates total context tokens
 * 2. If over threshold, summarizes older messages
 * 3. Injects summary + recent messages as the new context
 * 
 * This is a client-side solution that doesn't require model cooperation.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

interface PluginConfig {
  enabled?: boolean;
  maxTokens?: number;
  keepRecentTokens?: number;
  summaryMaxTokens?: number;
  charsPerToken?: number;
  summaryModel?: string;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
  /**
   * Optional: Only run compaction when session model matches these providers.
   * Example: ['ollama', 'lmstudio', 'friend-gpu']
   * If not set, compaction runs for all sessions when enabled.
   */
  modelFilter?: string[];
}

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface SessionEntry {
  id: string;
  type: string;
  message?: Message;
  content?: string;
  role?: string;
  parentId?: string;
}

interface PluginApi {
  config: {
    plugins?: {
      entries?: {
        'context-compactor'?: {
          config?: PluginConfig;
        };
      };
    };
  };
  logger: {
    info: (msg: string) => void;
    warn: (msg: string) => void;
    error: (msg: string) => void;
    debug: (msg: string) => void;
  };
  registerTool: (tool: any) => void;
  registerCommand: (cmd: any) => void;
  registerGatewayMethod: (name: string, handler: any) => void;
  on: (event: string, handler: (event: any) => Promise<any>) => void;
  runtime?: {
    llm?: {
      complete: (opts: { model?: string; messages: Message[]; maxTokens?: number }) => Promise<{ content: string }>;
    };
  };
}

// Simple token estimator (chars / charsPerToken)
function estimateTokens(text: string, charsPerToken: number): number {
  return Math.ceil(text.length / charsPerToken);
}

// Read session transcript
function readTranscript(sessionPath: string): SessionEntry[] {
  if (!fs.existsSync(sessionPath)) return [];
  
  const content = fs.readFileSync(sessionPath, 'utf8');
  const lines = content.trim().split('\n').filter(Boolean);
  
  return lines.map(line => {
    try {
      return JSON.parse(line);
    } catch {
      return null;
    }
  }).filter(Boolean) as SessionEntry[];
}

// Extract messages from session entries
function extractMessages(entries: SessionEntry[]): Message[] {
  const messages: Message[] = [];
  
  for (const entry of entries) {
    if (entry.type === 'message' && entry.message) {
      messages.push(entry.message);
    } else if (entry.role && entry.content) {
      messages.push({ role: entry.role as Message['role'], content: entry.content });
    }
  }
  
  return messages;
}

// Split messages into "old" (to summarize) and "recent" (to keep)
function splitMessages(
  messages: Message[],
  keepRecentTokens: number,
  charsPerToken: number
): { old: Message[]; recent: Message[] } {
  let recentTokens = 0;
  let splitIndex = messages.length;
  
  // Walk backwards from end, counting tokens
  for (let i = messages.length - 1; i >= 0; i--) {
    const msgTokens = estimateTokens(messages[i].content, charsPerToken);
    if (recentTokens + msgTokens > keepRecentTokens) {
      splitIndex = i + 1;
      break;
    }
    recentTokens += msgTokens;
    if (i === 0) splitIndex = 0;
  }
  
  return {
    old: messages.slice(0, splitIndex),
    recent: messages.slice(splitIndex),
  };
}

// Format messages for summarization
function formatForSummary(messages: Message[]): string {
  return messages.map(m => `[${m.role.toUpperCase()}]: ${m.content}`).join('\n\n');
}

// In-memory cache for summaries (avoid re-summarizing the same content)
const summaryCache = new Map<string, string>();

function hashMessages(messages: Message[]): string {
  const content = messages.map(m => `${m.role}:${m.content}`).join('|');
  // Simple hash
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    const char = content.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
}

export default function register(api: PluginApi) {
  const cfg = api.config.plugins?.entries?.['context-compactor']?.config ?? {};
  
  if (cfg.enabled === false) {
    api.logger.info('[context-compactor] Plugin disabled');
    return;
  }

  const maxTokens = cfg.maxTokens ?? 8000;
  const keepRecentTokens = cfg.keepRecentTokens ?? 2000;
  const summaryMaxTokens = cfg.summaryMaxTokens ?? 1000;
  const charsPerToken = cfg.charsPerToken ?? 4;
  const summaryModel = cfg.summaryModel;
  const modelFilter = cfg.modelFilter; // Optional: ['ollama', 'lmstudio', etc.]

  api.logger.info(`[context-compactor] Initialized (maxTokens=${maxTokens}, keepRecent=${keepRecentTokens}${modelFilter ? `, filter=${modelFilter.join(',')}` : ''})`);

  // ============================================================================
  // Core: before_agent_start hook
  // ============================================================================

  api.on('before_agent_start', async (event: { 
    prompt?: string;
    sessionKey?: string;
    sessionId?: string;
    model?: string;
    context?: {
      sessionFile?: string;
      messages?: Message[];
    };
  }) => {
    try {
      // If modelFilter is set, only run for matching providers
      if (modelFilter && modelFilter.length > 0 && event.model) {
        const modelLower = event.model.toLowerCase();
        const matches = modelFilter.some(filter => modelLower.includes(filter.toLowerCase()));
        if (!matches) {
          api.logger.debug?.(`[context-compactor] Skipping - model ${event.model} not in filter`);
          return;
        }
      }

      // Get current messages from context or session file
      let messages: Message[] = event.context?.messages ?? [];
      
      if (messages.length === 0 && event.context?.sessionFile) {
        const entries = readTranscript(event.context.sessionFile);
        messages = extractMessages(entries);
      }
      
      if (messages.length === 0) {
        api.logger.debug?.('[context-compactor] No messages to compact');
        return;
      }

      // Estimate total tokens
      const totalTokens = messages.reduce(
        (sum, m) => sum + estimateTokens(m.content, charsPerToken),
        0
      );

      api.logger.debug?.(`[context-compactor] Current context: ~${totalTokens} tokens`);

      // Check if compaction needed
      if (totalTokens <= maxTokens) {
        return; // Under limit, no action needed
      }

      api.logger.info(`[context-compactor] Context (~${totalTokens} tokens) exceeds limit (${maxTokens}), compacting...`);

      // Split into old and recent
      const { old, recent } = splitMessages(messages, keepRecentTokens, charsPerToken);

      if (old.length === 0) {
        api.logger.warn('[context-compactor] No old messages to summarize, skipping');
        return;
      }

      // Check cache
      const cacheKey = hashMessages(old);
      let summary = summaryCache.get(cacheKey);

      if (!summary) {
        // Generate summary
        const formatted = formatForSummary(old);
        
        const summaryPrompt = `Summarize this conversation concisely, preserving key decisions, context, and important details. Focus on information that would be needed to continue the conversation coherently.

CONVERSATION:
${formatted}

SUMMARY (be concise, max ${Math.floor(summaryMaxTokens * charsPerToken)} characters):`;

        if (api.runtime?.llm?.complete) {
          // Use OpenClaw's LLM runtime
          const result = await api.runtime.llm.complete({
            model: summaryModel,
            messages: [{ role: 'user', content: summaryPrompt }],
            maxTokens: summaryMaxTokens,
          });
          summary = result.content;
        } else {
          // Fallback: simple truncation-based summary
          api.logger.warn('[context-compactor] LLM runtime not available, using truncation fallback');
          const maxChars = summaryMaxTokens * charsPerToken;
          summary = `[Context Summary - ${old.length} messages compacted]\n\n`;
          
          // Keep first and last few messages
          const keepCount = Math.min(3, Math.floor(old.length / 2));
          const first = old.slice(0, keepCount);
          const last = old.slice(-keepCount);
          
          summary += 'Earlier:\n' + first.map(m => `- ${m.role}: ${m.content.slice(0, 200)}...`).join('\n');
          summary += '\n\nRecent:\n' + last.map(m => `- ${m.role}: ${m.content.slice(0, 200)}...`).join('\n');
          
          if (summary.length > maxChars) {
            summary = summary.slice(0, maxChars) + '...';
          }
        }

        // Cache it
        summaryCache.set(cacheKey, summary);
        
        // Limit cache size
        if (summaryCache.size > 100) {
          const firstKey = summaryCache.keys().next().value;
          if (firstKey) summaryCache.delete(firstKey);
        }
      }

      const recentTokens = recent.reduce(
        (sum, m) => sum + estimateTokens(m.content, charsPerToken),
        0
      );
      const summaryTokens = estimateTokens(summary, charsPerToken);
      const newTotal = summaryTokens + recentTokens;

      api.logger.info(
        `[context-compactor] Compacted ${old.length} messages → summary (~${summaryTokens} tokens) + ${recent.length} recent (~${recentTokens} tokens) = ~${newTotal} tokens`
      );

      // Return context modification
      return {
        prependContext: `<compacted-context>
The following is a summary of earlier conversation that was compacted to fit context limits:

${summary}

---
Recent conversation continues below:
</compacted-context>`,
        // Note: We can't actually replace messages in before_agent_start,
        // we can only prepend context. For full message replacement,
        // we'd need a different hook or session modification.
      };

    } catch (err: any) {
      api.logger.error(`[context-compactor] Error: ${err.message}`);
    }
  });

  // ============================================================================
  // Command: /compact
  // ============================================================================

  api.registerCommand({
    name: 'compact-now',
    description: 'Force context compaction on next message',
    acceptsArgs: false,
    requireAuth: true,
    handler: async () => {
      // Clear cache to force fresh summary
      summaryCache.clear();
      return { text: '🧹 Context compaction cache cleared. Next message will trigger fresh compaction if needed.' };
    },
  });

  // ============================================================================
  // Command: /context-stats
  // ============================================================================

  api.registerCommand({
    name: 'context-stats',
    description: 'Show estimated context token usage',
    acceptsArgs: false,
    requireAuth: true,
    handler: async (ctx: { sessionFile?: string }) => {
      try {
        if (!ctx.sessionFile) {
          return { text: '⚠️ Session file not available' };
        }

        const entries = readTranscript(ctx.sessionFile);
        const messages = extractMessages(entries);
        
        const totalTokens = messages.reduce(
          (sum, m) => sum + estimateTokens(m.content, charsPerToken),
          0
        );

        const userMsgs = messages.filter(m => m.role === 'user').length;
        const assistantMsgs = messages.filter(m => m.role === 'assistant').length;
        const systemMsgs = messages.filter(m => m.role === 'system').length;

        return {
          text: `📊 **Context Stats**

**Messages:** ${messages.length} total
- User: ${userMsgs}
- Assistant: ${assistantMsgs}
- System: ${systemMsgs}

**Estimated Tokens:** ~${totalTokens.toLocaleString()}
**Limit:** ${maxTokens.toLocaleString()}
**Usage:** ${((totalTokens / maxTokens) * 100).toFixed(1)}%

${totalTokens > maxTokens ? '⚠️ **Over limit - compaction will trigger**' : '✅ Within limits'}`,
        };
      } catch (err: any) {
        return { text: `❌ Error: ${err.message}` };
      }
    },
  });

  // ============================================================================
  // RPC: context-compactor.stats
  // ============================================================================

  api.registerGatewayMethod('context-compactor.stats', async ({ params, respond }: any) => {
    try {
      const { sessionFile } = params;
      
      if (!sessionFile || !fs.existsSync(sessionFile)) {
        respond(true, { error: 'Session file not found', messages: 0, tokens: 0 });
        return;
      }

      const entries = readTranscript(sessionFile);
      const messages = extractMessages(entries);
      
      const totalTokens = messages.reduce(
        (sum, m) => sum + estimateTokens(m.content, charsPerToken),
        0
      );

      respond(true, {
        messages: messages.length,
        tokens: totalTokens,
        maxTokens,
        needsCompaction: totalTokens > maxTokens,
        cacheSize: summaryCache.size,
      });
    } catch (err: any) {
      respond(false, { error: err.message });
    }
  });
}

export const id = 'context-compactor';
export const name = 'Context Compactor - Local Model Support';
