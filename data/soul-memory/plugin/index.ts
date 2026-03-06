/**
 * Soul Memory Plugin for OpenClaw
 * 
 * Automatically injects Soul Memory search results before each response
 * using the before_prompt_build Hook.
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Soul Memory configuration
interface SoulMemoryConfig {
  enabled: boolean;
  topK: number;
  minScore: number;
}

// Search result from Soul Memory
interface MemoryResult {
  path: string;
  content: string;
  score: number;
  priority?: string;
}

/**
 * Search Soul Memory using Python backend
 */
async function searchMemories(query: string, config: SoulMemoryConfig): Promise<MemoryResult[]> {
  try {
    const { stdout } = await execAsync(
      `python3 /root/.openclaw/workspace/soul-memory/cli.py search "${query}" --top_k ${config.topK} --min_score ${config.minScore}`,
      { timeout: 5000 } // 5 second timeout
    );

    // Parse JSON output
    const results = JSON.parse(stdout || '[]');
    return Array.isArray(results) ? results : [];
  } catch (error) {
    // Silently fail on errors to avoid breaking the agent
    console.error('[Soul Memory] Search failed:', error instanceof Error ? error.message : String(error));
    return [];
  }
}

/**
 * Build memory context string from results with marking
 * Uses SoulM delimiters to enable cleanup on next injection
 */
function buildMemoryContext(results: MemoryResult[]): string {
  if (results.length === 0) {
    return '';
  }

  // Add marker at the beginning
  let context = '\nSoulM"';

  // Build content
  let content = '';
  results.forEach((result, index) => {
    const scoreBadge = result.score > 5 ? '🔥' : result.score > 3 ? '⭐' : '';
    const priorityBadge = result.priority === 'C' ? '[🔴 Critical]'
                        : result.priority === 'I' ? '[🟡 Important]'
                        : '';

    content += `${index + 1}. ${scoreBadge} ${priorityBadge} ${result.content}\n`;

    if (result.path && result.score > 3) {
      content += `   *Source: ${result.path}*\n`;
    }
    content += '\n';
  });

  // Wrap final marker
  context += content + '"\n';

  return context;
}

/**
 * Get the last user message from the conversation
 */
function getLastUserMessage(messages: any[]): string {
  if (!messages || messages.length === 0) {
    return '';
  }

  // Find the last message from user role
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg.role === 'user' && msg.content) {
      // Handle different content formats
      if (Array.isArray(msg.content)) {
        return msg.content
          .filter((item: any) => item.type === 'text')
          .map((item: any) => item.text)
          .join(' ');
      } else if (typeof msg.content === 'string') {
        return msg.content;
      }
    }
  }

  return '';
}

/**
 * Extract query from user message, removing metadata blocks and old memory markers
 */
function extractQuery(rawMessage: string): string {
  if (!rawMessage) return '';

  let cleaned = rawMessage.trim();

  // CRITICAL 1: Remove old memory marked with SoulM delimiters
  // Pattern: SoulM"...content..."
  cleaned = cleaned.replace(/SoulM".*?"/gs, '');

  // CRITICAL 2: Remove legacy memory context explicitly
  // Pattern: ## 🧠 Memory Context... (all content until next major section)
  cleaned = cleaned.replace(/## 🧠 Memory Context[\s\S]*?(?=\n\n\s*\n|$|## |---)/gm, '');
  cleaned = cleaned.replace(/🧠 Memory Context[\s\S]*?(?=\n\n\s*\n|$|## |---)/gm, '');

  // CRITICAL 3: Remove numbered memory entries (e.g., "1. 🔥 [🔴 Critical]...")
  cleaned = cleaned.replace(/^\s*\d+\.\s+🔥.*$/gm, '');
  cleaned = cleaned.replace(/^\s*\d+\.\s+⭐.*$/gm, '');

  // Remove "Conversation info" metadata blocks
  cleaned = cleaned.replace(/Conversation info \(untrusted metadata\):[\s\S]*?\n\n/g, '');

  // Remove "System:" messages
  cleaned = cleaned.replace(/^System: \[[\s\S]*?\]$/gm, '');

  // Remove Markdown code blocks (```json ... ```, ``` ... ```)
  cleaned = cleaned.replace(/```[\s\S]*?```/g, '');

  // Remove HTML/XML-like blocks
  cleaned = cleaned.replace(/<[\s\S]*?>/g, '');

  // Remove empty lines and clean up
  cleaned = cleaned.replace(/\n\s*\n/g, '\n').trim();

  // If after cleaning we have nothing, use a longer prefix of the original message
  if (cleaned.length < 5 && rawMessage.length > 10) {
    // Try to extract the first meaningful sentence
    const firstSentenceMatch = rawMessage.match(/^[^。!！?？\n]+[。!！?？]?/);
    if (firstSentenceMatch) {
      cleaned = firstSentenceMatch[0].trim();
    } else {
      // Fallback to first 200 characters
      cleaned = rawMessage.substring(0, 200).trim();
    }
  }

  // Limit to 200 characters
  return cleaned.substring(0, 200);
}

/**
 * Clean old memory markers from messages array
 * This prevents accumulation of memory context in conversation history
 */
function cleanOldMemoryFromMessages(messages: any[]): any[] {
  if (!messages || messages.length === 0) {
    return messages;
  }

  let cleanedMessages = [];
  let hadOldMemory = false;

  messages.forEach(msg => {
    let cleanedMsg = { ...msg };

    // Clean user messages
    if (msg.role === 'user') {
      let content = '';

      if (typeof msg.content === 'string') {
        content = msg.content;
      } else if (Array.isArray(msg.content)) {
        content = msg.content
          .filter((item: any) => item.type === 'text')
          .map((item: any) => item.text)
          .join(' ');
      }

      // Remove old memory markers
      const originalContent = content;
      content = content.replace(/SoulM".*?"/gs, '');

      // Check if we removed anything
      if (originalContent !== content) {
        hadOldMemory = true;

        // Update message content
        if (typeof msg.content === 'string') {
          cleanedMsg.content = content;
        } else if (Array.isArray(msg.content)) {
          cleanedMsg.content = msg.content.map((item: any) => {
            if (item.type === 'text') {
              return { type: 'text', text: content };
            }
            return item;
          });
        }
      }
    }

    // Clean assistant messages (remove SoulM markers)
    if (msg.role === 'assistant' && typeof msg.content === 'string') {
      const originalContent = msg.content;
      const cleanedContent = msg.content.replace(/SoulM".*?"/gs, '');

      if (originalContent !== cleanedContent) {
        hadOldMemory = true;
        cleanedMsg.content = cleanedContent;
      }
    }

    cleanedMessages.push(cleanedMsg);
  });

  if (hadOldMemory) {
    console.log('[Soul Memory] ✓ Cleaned old memory markers from messages');
  }

  return cleanedMessages;
}

/**
 * Plugin entry point
 */
export default function register(api: any) {
  const logger = api.logger || console;

  logger.info('[Soul Memory] Plugin registered via api.register()');

  // Register before_prompt_build Hook using api.on() (Plugin Hook API)
  api.on('before_prompt_build', async (event: any, ctx: any) => {
    const config: SoulMemoryConfig = {
      enabled: true,
      topK: 5,
      minScore: 0.0,
      ...api.config.plugins?.entries?.['soul-memory']?.config
    };

    // IMPORTANT: Log that hook was called
    logger.info('[Soul Memory] ✓ BEFORE_PROMPT_BUILD HOOK CALLED via api.on()');
    logger.debug(`[Soul Memory] Config: enabled=${config.enabled}, topK=${config.topK}, minScore=${config.minScore}`);
    logger.debug(`[Soul Memory] Event: prompt=${event.prompt?.substring(0, 50)}..., messages=${event.messages?.length || 0}`);
    logger.debug(`[Soul Memory] Context: agentId=${ctx.agentId}, sessionKey=${ctx.sessionKey}`);

    // Check if enabled
    if (!config.enabled) {
      logger.info('[Soul Memory] Plugin disabled, skipping');
      return {};
    }

    // CRITICAL: Extract query from prompt, not from messages history
    // Messages may contain injected memory from previous turns
    const prompt = event.prompt || '';

    // Extract query from the last line of prompt (user's actual question)
    let userQuery = prompt.trim();

    // Get the last line (user's current question)
    const lastNewlineIndex = userQuery.lastIndexOf('\n');
    if (lastNewlineIndex >= 0) {
      userQuery = userQuery.substring(lastNewlineIndex + 1).trim();
    }

    // If prompt is empty, try to get from messages as fallback
    let lastUserMessage = userQuery;
    if (!lastUserMessage || lastUserMessage.length === 0) {
      logger.debug('[Soul Memory] Prompt is empty, falling back to messages');
      const messages = event.messages || [];
      const cleanedMessages = cleanOldMemoryFromMessages(messages);
      lastUserMessage = getLastUserMessage(cleanedMessages);
    }

    logger.debug(`[Soul Memory] User query length: ${lastUserMessage.length}`);

    // Skip if no user query
    if (!lastUserMessage || lastUserMessage.trim().length === 0) {
      logger.debug('[Soul Memory] No user query found, skipping');
      return {};
    }

    // Extract query with metadata removal
    const query = extractQuery(lastUserMessage);

    // Skip if query is too short
    if (query.length < 5) {
      logger.debug(`[Soul Memory] Query too short (${query.length} chars): "${query}", skipping`);
      return {};
    }

    logger.info(`[Soul Memory] Searching for: "${query}"`);

    // Search memories
    const results = await searchMemories(query, config);

    logger.info(`[Soul Memory] Found ${results.length} results`);

    if (results.length === 0) {
      logger.info('[Soul Memory] No memories found');
      return {};
    }

    // Build memory context with marking
    const memoryContext = buildMemoryContext(results);

    logger.info(`[Soul Memory] ✓ Injected ${results.length} memories with SoulM delimiters (${memoryContext.length} chars)`);

    // Return with prependContext
    return {
      prependContext: memoryContext
    };
  });

  logger.info('[Soul Memory] Hook registered via api.on(): before_prompt_build');
}
