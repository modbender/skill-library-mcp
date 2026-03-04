/**
 * Development server - Voice API with Function Calling
 * 
 * BRANCH: voice-function-calling
 * 
 * Uses Telnyx Inference (Qwen) with native function calling.
 * Tools executed locally via CLI for speed.
 * 
 * Expected latency: ~500ms-1.5s (vs 6-10s with Haiku)
 */

import 'dotenv/config';
import express from 'express';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { startTunnel, stopTunnel } from './tunnel.js';
import { ChildProcess } from 'child_process';
import OpenAI from 'openai';

const execAsync = promisify(exec);

const PORT = parseInt(process.env.PORT || '3000', 10);
const TELNYX_API_KEY = process.env.TELNYX_API_KEY || '';
const ENABLE_TUNNEL = process.env.ENABLE_TUNNEL !== 'false';

// Telnyx Inference API (direct, fast)
const TELNYX_INFERENCE_URL = 'https://api.telnyx.com/v2/ai/chat/completions';

// OpenAI SDK client for Telnyx Inference (handles extra_body properly)
const openaiClient = new OpenAI({
  apiKey: TELNYX_API_KEY,
  baseURL: 'https://api.telnyx.com/v2/ai',
});

// Model - Qwen for function calling (only model with tool support on Telnyx)
const VOICE_MODEL = process.env.VOICE_MODEL || 'Qwen/Qwen3-235B-A22B';
const TTS_VOICE = process.env.TTS_VOICE || 'Polly.Amy-Neural';

// Personalization - loaded from workspace files or env fallback
let ASSISTANT_NAME = process.env.ASSISTANT_NAME || 'Assistant';
let USER_NAME = process.env.USER_NAME || 'User';
let USER_TIMEZONE = process.env.USER_TIMEZONE || 'Europe/Dublin';

// Gateway config for /tools/invoke API (for cross-channel messaging)
let GATEWAY_URL = 'http://127.0.0.1:18789';
let GATEWAY_TOKEN = '';

// Load personalization from workspace files (IDENTITY.md, USER.md)
async function loadPersonalization(): Promise<void> {
  const workspace = process.env.WORKSPACE_DIR || process.cwd();
  const fs = await import('fs/promises');
  
  // Load IDENTITY.md for assistant name
  try {
    const identityPath = `${workspace}/IDENTITY.md`;
    const identity = await fs.readFile(identityPath, 'utf-8');
    const nameMatch = identity.match(/\*\*Name:\*\*\s*(.+)/i) || identity.match(/^-\s*\*\*Name:\*\*\s*(.+)/mi);
    if (nameMatch) {
      ASSISTANT_NAME = nameMatch[1].trim();
      console.log(`  📛 Loaded assistant name: ${ASSISTANT_NAME}`);
    }
  } catch {
    // IDENTITY.md not found, use env/default
  }
  
  // Load USER.md for user name and timezone
  try {
    const userPath = `${workspace}/USER.md`;
    const user = await fs.readFile(userPath, 'utf-8');
    
    // Try "What to call them" first, then "Name"
    const callMatch = user.match(/\*\*What to call them:\*\*\s*(.+)/i);
    const nameMatch = user.match(/\*\*Name:\*\*\s*(.+)/i);
    if (callMatch) {
      USER_NAME = callMatch[1].trim();
      console.log(`  👤 Loaded user name: ${USER_NAME}`);
    } else if (nameMatch) {
      USER_NAME = nameMatch[1].split(/\s+/)[0].trim(); // First name only
      console.log(`  👤 Loaded user name: ${USER_NAME}`);
    }
    
    const tzMatch = user.match(/\*\*Timezone:\*\*\s*(.+)/i);
    if (tzMatch) {
      USER_TIMEZONE = tzMatch[1].trim();
      console.log(`  🌍 Loaded timezone: ${USER_TIMEZONE}`);
    }
  } catch {
    // USER.md not found, use env/default
  }
}

// Load gateway config from OpenClaw config file
async function loadGatewayConfig(): Promise<void> {
  const fs = await import('fs/promises');
  const homedir = process.env.HOME || '/home/node';
  
  // Try multiple config paths (OpenClaw, then legacy Clawdbot)
  const configPaths = [
    `${homedir}/.openclaw/openclaw.json`,
    `${homedir}/.clawdbot/clawdbot.json`,
  ];
  
  for (const configPath of configPaths) {
    try {
      const configData = await fs.readFile(configPath, 'utf-8');
      const config = JSON.parse(configData);
      
      const port = config.gateway?.port || 18789;
      GATEWAY_URL = `http://127.0.0.1:${port}`;
      GATEWAY_TOKEN = config.gateway?.auth?.token || '';
      
      console.log(`  🔌 Loaded gateway config from ${configPath}`);
      console.log(`  🔌 Gateway URL: ${GATEWAY_URL}`);
      return;
    } catch {
      // Config not found at this path, try next
    }
  }
  
  console.log(`  ⚠️ No gateway config found, using defaults`);
}

const app = express();
app.use(express.json());

// ============================================================================
// TOOL DEFINITIONS
// ============================================================================

interface ToolDefinition {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: Record<string, any>;
      required?: string[];
    };
  };
}

const tools: ToolDefinition[] = [
  {
    type: 'function',
    function: {
      name: 'list_cron_jobs',
      description: 'LIST all scheduled cron jobs, reminders, and tasks. USE THIS when user asks: "what cron jobs", "what reminders", "show my schedule", "what tasks are running". Returns a list of all active jobs.',
      parameters: {
        type: 'object',
        properties: {},
        required: [],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'add_reminder',
      description: 'CREATE a new reminder or scheduled task. Use when user explicitly asks to ADD, SET, or CREATE a reminder.',
      parameters: {
        type: 'object',
        properties: {
          message: {
            type: 'string',
            description: 'The reminder message or task description',
          },
          time: {
            type: 'string',
            description: 'When to trigger the reminder. Can be relative (e.g., "in 5 minutes", "in 1 hour", "tomorrow at 9am") or a cron expression for recurring tasks.',
          },
          channel: {
            type: 'string',
            description: 'Optional: channel to deliver the reminder (e.g., slack, whatsapp, discord, telegram). If not specified, uses the default configured channel.',
          },
        },
        required: ['message', 'time'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'remove_cron_job',
      description: 'DELETE/REMOVE an existing cron job or reminder. ONLY use when user explicitly asks to DELETE, REMOVE, or CANCEL a specific job. Requires the job name or ID.',
      parameters: {
        type: 'object',
        properties: {
          identifier: {
            type: 'string',
            description: 'The exact name or ID of the cron job to remove.',
          },
        },
        required: ['identifier'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'get_weather',
      description: 'Get current weather and forecast for a location. Use this when the user asks about weather.',
      parameters: {
        type: 'object',
        properties: {
          location: {
            type: 'string',
            description: 'The city or location to get weather for. Defaults to Dublin if not specified.',
          },
        },
        required: [],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'search_memory',
      description: 'Search through memory and notes for information. Use this when the user asks about something that might be in their notes, previous conversations, or stored information.',
      parameters: {
        type: 'object',
        properties: {
          query: {
            type: 'string',
            description: 'What to search for in memory',
          },
        },
        required: ['query'],
      },
    },
  },
  {
    type: 'function',
    function: {
      name: 'send_message',
      description: 'Send a message to a specific person or channel. ALWAYS extract who the message should go to. If user says "send to the team" or "send to everyone", ask which channel/person.',
      parameters: {
        type: 'object',
        properties: {
          message: {
            type: 'string',
            description: 'The message content to send',
          },
          channel: {
            type: 'string',
            description: 'The messaging platform: slack, telegram, whatsapp, discord, signal, or imessage. Default: slack',
          },
          to: {
            type: 'string',
            description: 'REQUIRED: The recipient. For Slack: person name (e.g. "User") or channel name (e.g. "engineering", "general"). For WhatsApp/Signal: phone number. Always include this field.',
          },
        },
        required: ['message', 'to'],
      },
    },
  },
];

// ============================================================================
// TOOL EXECUTION
// ============================================================================

async function executeTool(name: string, args: Record<string, any>): Promise<string> {
  console.log(`  🔧 Executing tool: ${name}(${JSON.stringify(args)})`);
  const startTime = Date.now();
  
  try {
    let result: string;
    
    switch (name) {
      case 'list_cron_jobs':
        result = await listCronJobs();
        break;
      case 'add_reminder':
        result = await addReminder(args.message, args.time, args.channel);
        break;
      case 'remove_cron_job':
        result = await removeCronJob(args.identifier);
        break;
      case 'get_weather':
        result = await getWeather(args.location);
        break;
      case 'search_memory':
        result = await searchMemory(args.query);
        break;
      case 'send_message':
        result = await sendMessage(args.message, args.channel, args.to);
        break;
      default:
        result = `Unknown tool: ${name}`;
    }
    
    const duration = Date.now() - startTime;
    console.log(`  ✅ Tool completed in ${duration}ms`);
    return result;
  } catch (error) {
    console.error(`  ❌ Tool error:`, error);
    return `Error executing ${name}: ${(error as Error).message}`;
  }
}

// Try multiple CLI names for compatibility (openclaw is latest, then clawdbot, then moltbook)
async function runCLI(args: string): Promise<string> {
  const cliNames = ['openclaw', 'clawdbot', 'moltbook'];
  let lastError: Error | null = null;
  
  for (const cli of cliNames) {
    try {
      const { stdout } = await execAsync(`${cli} ${args}`);
      return stdout;
    } catch (err: any) {
      if (err.message?.includes('command not found') || err.code === 127) {
        lastError = err;
        continue; // Try next CLI
      }
      throw err; // Other error, propagate it
    }
  }
  
  throw lastError || new Error('No CLI found (tried: openclaw, clawdbot, moltbook)');
}

async function listCronJobs(): Promise<string> {
  const stdout = await runCLI('cron list --json');
  const data = JSON.parse(stdout);
  
  if (!data.jobs || data.jobs.length === 0) {
    return 'No cron jobs or reminders are currently scheduled.';
  }
  
  const jobs = data.jobs.map((job: any) => {
    const schedule = job.schedule.kind === 'cron' 
      ? `recurring (${job.schedule.expr})`
      : job.schedule.kind === 'at'
        ? `one-time at ${new Date(job.schedule.atMs).toLocaleString('en-IE', { timeZone: USER_TIMEZONE })}`
        : job.schedule.kind;
    
    return {
      name: job.name,
      enabled: job.enabled,
      schedule,
      message: job.payload?.message?.substring(0, 100),
    };
  });
  
  return JSON.stringify({ jobs, count: jobs.length }, null, 2);
}

async function addReminder(message: string, time: string, channel: string = 'slack'): Promise<string> {
  // Parse relative time to absolute
  let scheduleArg = '';
  const lower = time.toLowerCase();
  
  if (lower.includes('in ')) {
    // Relative time: "in 5 minutes", "in 1 hour"
    const match = lower.match(/in\s+(\d+)\s*(min|minute|hour|hr|day|week)/i);
    if (match) {
      const num = parseInt(match[1]);
      const unit = match[2].toLowerCase();
      const ms = unit.startsWith('min') ? num * 60000
        : unit.startsWith('hour') || unit === 'hr' ? num * 3600000
        : unit.startsWith('day') ? num * 86400000
        : unit.startsWith('week') ? num * 604800000
        : 0;
      const targetTime = new Date(Date.now() + ms);
      scheduleArg = `--at "${targetTime.toISOString()}"`;
    }
  } else if (lower.includes('tomorrow')) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    // Try to parse time from "tomorrow at 9am"
    const timeMatch = lower.match(/(\d{1,2})(?::(\d{2}))?\s*(am|pm)?/i);
    if (timeMatch) {
      let hours = parseInt(timeMatch[1]);
      const minutes = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
      const ampm = timeMatch[3]?.toLowerCase();
      if (ampm === 'pm' && hours < 12) hours += 12;
      if (ampm === 'am' && hours === 12) hours = 0;
      tomorrow.setHours(hours, minutes, 0, 0);
    } else {
      tomorrow.setHours(9, 0, 0, 0); // Default to 9am
    }
    scheduleArg = `--at "${tomorrow.toISOString()}"`;
  } else {
    // Assume it's a cron expression or specific time
    scheduleArg = `--at "${time}"`;
  }
  
  const channelArg = channel ? `--channel ${channel}` : '';
  const name = `Voice Reminder: ${message.substring(0, 30)}`;
  
  const cronArgs = `cron add ${scheduleArg} ${channelArg} --name "${name}" --message "${message.replace(/"/g, '\\"')}"`.replace(/\s+/g, ' ').trim();
  console.log(`  📝 Running: [cli] ${cronArgs}`);
  
  await runCLI(cronArgs);
  
  return `Reminder set: "${message}" - scheduled for ${time}`;
}

async function removeCronJob(identifier: string): Promise<string> {
  // First, list jobs to find matching one
  const stdout = await runCLI('cron list --json');
  const data = JSON.parse(stdout);
  
  const lowerIdent = identifier.toLowerCase();
  const job = data.jobs?.find((j: any) => 
    j.id === identifier || 
    j.name?.toLowerCase().includes(lowerIdent) ||
    j.payload?.message?.toLowerCase().includes(lowerIdent)
  );
  
  if (!job) {
    return `Could not find a cron job matching "${identifier}"`;
  }
  
  await runCLI(`cron rm ${job.id}`);
  return `Removed cron job: ${job.name}`;
}

async function getWeather(location: string = 'Dublin'): Promise<string> {
  const loc = location || 'Dublin';
  // Use simpler format for faster response
  const url = `https://wttr.in/${encodeURIComponent(loc)}?format=%l:+%c+%t+(feels+like+%f),+%C,+%h+humidity,+wind+%w`;
  
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 3000); // 3s timeout
  
  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timeout);
    
    if (!response.ok) {
      return `Could not get weather for ${loc}`;
    }
    
    const text = await response.text();
    return text.trim() || `Weather data unavailable for ${loc}`;
  } catch (error) {
    clearTimeout(timeout);
    return `Weather request timed out for ${loc}`;
  }
}

async function searchMemory(query: string): Promise<string> {
  // Use fast grep for voice (embeddings too slow for real-time)
  // Search key memory files with multiple keywords
  const workspace = process.env.WORKSPACE_DIR || process.cwd();
  const memoryDir = `${workspace}/memory`;
  const mainMemory = `${workspace}/MEMORY.md`;
  
  // Extract keywords from query for better grep matching
  const keywords = query.toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(w => w.length > 3 && !['what', 'have', 'been', 'working', 'lately', 'tell', 'about', 'the'].includes(w));
  
  // If no useful keywords, search for common project terms
  const searchTerms = keywords.length > 0 ? keywords : ['segue', 'webrtc', 'voice', 'project'];
  
  try {
    const results: string[] = [];
    
    for (const term of searchTerms.slice(0, 3)) {
      try {
        const { stdout } = await execAsync(
          `grep -r -i -l "${term}" ${memoryDir} ${mainMemory} 2>/dev/null | head -3`,
          { timeout: 3000 }
        );
        
        if (stdout.trim()) {
          const files = stdout.trim().split('\n');
          for (const file of files.slice(0, 2)) {
            const { stdout: content } = await execAsync(
              `grep -i -B 1 -A 3 "${term}" "${file}" 2>/dev/null | head -15`,
              { timeout: 2000 }
            );
            if (content.trim() && !results.some(r => r.includes(content.trim().slice(0, 50)))) {
              results.push(`From ${file.replace(workspace + '/', '')}:\n${content.trim()}`);
            }
          }
        }
      } catch {
        // Skip failed searches
      }
    }
    
    if (results.length === 0) {
      return `No memory entries found matching "${query}"`;
    }
    
    return results.slice(0, 3).join('\n\n');
  } catch {
    return `No memory entries found matching "${query}"`;
  }
}

async function sendMessage(message: string, channel: string = 'slack', to?: string): Promise<string> {
  try {
    // Route through gateway's /v1/chat/completions endpoint (like ClawdTalk)
    // This lets the gateway agent handle channel name resolution with full permissions
    const chatUrl = `${GATEWAY_URL}/v1/chat/completions`;
    
    // Build the instruction for the gateway agent
    const channelName = channel?.toLowerCase() || 'slack';
    const targetPart = to ? ` to ${to}` : '';
    const instruction = `Send a ${channelName} message${targetPart}: "${message}"`;
    
    console.log(`  📤 Sending message via gateway agent: ${instruction}`);
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'x-openclaw-agent-id': 'main',  // Use main agent context
    };
    
    if (GATEWAY_TOKEN) {
      headers['Authorization'] = `Bearer ${GATEWAY_TOKEN}`;
    }
    
    const response = await fetch(chatUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        model: 'anthropic/claude-sonnet-4-20250514',  // Fast model for simple task
        messages: [
          { role: 'user', content: instruction }
        ],
        max_tokens: 150,
      }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Gateway error: ${response.status} - ${errorText}`);
    }
    
    const result = await response.json();
    const assistantReply = result.choices?.[0]?.message?.content || '';
    
    // Check if the reply indicates success
    if (assistantReply.toLowerCase().includes('sent') || assistantReply.toLowerCase().includes('delivered')) {
      const recipient = to ? ` to ${to}` : '';
      return `Message sent${recipient} via ${channel}: "${message}"`;
    } else if (assistantReply.toLowerCase().includes('error') || assistantReply.toLowerCase().includes('failed')) {
      throw new Error(assistantReply);
    }
    
    // Assume success if no error indicators
    const recipient = to ? ` to ${to}` : '';
    return `Message sent${recipient} via ${channel}: "${message}"`;
  } catch (error: any) {
    console.error(`  ❌ Send message error:`, error.message);
    return `Failed to send message: ${error.message}`;
  }
}

// ============================================================================
// CALL STATE & VOICE
// ============================================================================

interface CallState {
  callControlId: string;
  from: string;
  to: string;
  messages: Array<{ role: 'user' | 'assistant' | 'system' | 'tool'; content: string; tool_call_id?: string; name?: string }>;
  startTime: Date;
  isProcessing: boolean;
  speakQueue: string[];
  isSpeaking: boolean;
  pendingInterrupt: boolean;
}
const activeCalls = new Map<string, CallState>();

function buildSystemPrompt(): string {
  const now = new Date().toLocaleString('en-IE', { 
    timeZone: USER_TIMEZONE, 
    hour: 'numeric', 
    minute: 'numeric',
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });
  
  return `You are ${ASSISTANT_NAME}, ${USER_NAME}'s AI assistant. This is a VOICE CALL.

Current time: ${now} (${USER_TIMEZONE})

PERSONALITY:
- Sharp, helpful, occasionally witty
- No sycophancy - just help
- Direct and concise

VOICE RULES (CRITICAL - FOLLOW EXACTLY):
- 1-3 sentences MAX per response
- Natural speech only - no markdown, no emojis, no bullet points
- DO NOT use <think> tags - respond directly without showing reasoning
- DO NOT include any XML tags in your response
- Keep responses under 50 words
- Talk like you're on the phone with a friend

YOU MUST USE TOOLS - THIS IS MANDATORY:

TOOL TRIGGERS (if user says ANY of these, you MUST call the tool):
- "cron", "reminders", "schedule", "tasks", "jobs" → call list_cron_jobs
- "remind me", "set a reminder", "alert me" → call add_reminder  
- "delete", "remove", "cancel" + job/reminder → call remove_cron_job
- "weather", "temperature", "forecast", "rain", "cold", "hot" → call get_weather
- "working on", "been doing", "projects", "memory", "notes", "history", "remember" → call search_memory

ABSOLUTE RULES:
1. If the question matches ANY trigger above, you MUST call the tool BEFORE responding
2. NEVER say "let me check" or "I'll look" without making a tool_call
3. NEVER guess or make up information - call the tool
4. After getting tool results, summarize them naturally in 1-2 sentences
5. If you don't call a tool when you should have, you have FAILED`;
}

let VOICE_SYSTEM_PROMPT = buildSystemPrompt();

async function callCommand(callControlId: string, command: string, params: Record<string, any> = {}) {
  const url = `https://api.telnyx.com/v2/calls/${callControlId}/actions/${command}`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TELNYX_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`${command} failed: ${error}`);
  }
  
  return response.json();
}

async function processSpeakQueue(call: CallState) {
  if (call.pendingInterrupt) {
    call.speakQueue = [];
    return;
  }
  if (call.isSpeaking || call.speakQueue.length === 0) return;
  
  call.isSpeaking = true;
  const text = call.speakQueue.shift()!;
  
  console.log(`  🔊 Speaking: "${text.substring(0, 60)}${text.length > 60 ? '...' : ''}"`);
  
  try {
    await callCommand(call.callControlId, 'speak', {
      payload: text,
      voice: TTS_VOICE,
      language: 'en-GB',
    });
  } catch (error) {
    console.error('  Speak error:', error);
    call.isSpeaking = false;
  }
}

async function interruptSpeaking(call: CallState) {
  if (!call.isSpeaking && call.speakQueue.length === 0) return;
  
  console.log(`  🛑 Barge-in detected, stopping audio...`);
  call.pendingInterrupt = true;
  call.isSpeaking = false;
  call.speakQueue = [];
  
  try {
    // Use speak with stop parameter + minimal payload (both required by API)
    // The stop: 'current' triggers immediately before the minimal payload plays
    await callCommand(call.callControlId, 'speak', { 
      stop: 'current',
      payload: '.',
      voice: TTS_VOICE,
    });
    console.log(`  ✅ Audio stopped`);
  } catch (error) {
    console.log(`  ⚠️ Stop audio failed:`, error);
    // Ignore - speak may have already finished
  }
}

function cleanResponseForSpeech(text: string): string {
  // Remove <think>...</think> tags (Qwen thinking mode)
  let clean = text.replace(/<think>[\s\S]*?<\/think>/gi, '').trim();
  
  // Remove any remaining XML-like tags
  clean = clean.replace(/<[^>]+>/g, '').trim();
  
  // Remove markdown
  clean = clean
    .replace(/\*\*([^*]+)\*\*/g, '$1')  // bold
    .replace(/\*([^*]+)\*/g, '$1')       // italic
    .replace(/`([^`]+)`/g, '$1')         // code
    .replace(/#{1,6}\s/g, '')            // headers
    .trim();
  
  // Truncate if too long (TTS max is 3000)
  if (clean.length > 2500) {
    clean = clean.substring(0, 2500) + '...';
  }
  
  return clean;
}

function queueSpeak(call: CallState, text: string) {
  const clean = cleanResponseForSpeech(text);
  if (!clean) return;
  call.speakQueue.push(clean);
  processSpeakQueue(call);
}

// ============================================================================
// LLM + FUNCTION CALLING
// ============================================================================

// Detect if we should force a specific tool based on keywords
function detectForcedTool(message: string): string | { type: string; function: { name: string } } {
  const lower = message.toLowerCase();
  
  // Memory/work questions → force search_memory
  if (
    lower.includes('working on') ||
    lower.includes('worked on') ||
    lower.includes('been doing') ||
    lower.includes('been up to') ||
    lower.includes('projects') ||
    lower.includes('today') && (lower.includes('we') || lower.includes('you') || lower.includes('i')) ||
    lower.includes('recently') ||
    lower.includes('remember') ||
    lower.includes('memory') ||
    lower.includes('notes')
  ) {
    console.log(`  🎯 Forcing tool: search_memory (keywords detected)`);
    return { type: 'function', function: { name: 'search_memory' } };
  }
  
  // Cron/schedule questions → force list_cron_jobs
  if (
    lower.includes('cron') ||
    lower.includes('reminders') ||
    lower.includes('scheduled') ||
    lower.includes('my schedule') ||
    lower.includes('tasks') ||
    (lower.includes('what') && lower.includes('jobs'))
  ) {
    console.log(`  🎯 Forcing tool: list_cron_jobs (keywords detected)`);
    return { type: 'function', function: { name: 'list_cron_jobs' } };
  }
  
  // Weather questions → force get_weather
  if (
    lower.includes('weather') ||
    lower.includes('temperature') ||
    lower.includes('forecast') ||
    lower.includes('rain') ||
    lower.includes('cold outside') ||
    lower.includes('hot outside')
  ) {
    console.log(`  🎯 Forcing tool: get_weather (keywords detected)`);
    return { type: 'function', function: { name: 'get_weather' } };
  }
  
  // Message sending → force send_message
  if (
    lower.includes('send a message') ||
    lower.includes('send message') ||
    lower.includes('text ') ||
    lower.includes('dm ') ||
    lower.includes('slack message') ||
    lower.includes('message on slack') ||
    lower.includes('whatsapp') ||
    lower.includes('telegram') ||
    lower.includes('signal') ||
    lower.includes('imessage')
  ) {
    console.log(`  🎯 Forcing tool: send_message (keywords detected)`);
    return { type: 'function', function: { name: 'send_message' } };
  }
  
  // Default: let the model decide
  return 'auto';
}

async function callLLMWithTools(call: CallState, userMessage: string): Promise<string> {
  const messages: any[] = [
    { role: 'system', content: VOICE_SYSTEM_PROMPT },
    ...call.messages,
    { role: 'user', content: userMessage },
  ];

  call.pendingInterrupt = false;
  const requestStart = Date.now();

  // Detect if we should force a specific tool
  const toolChoice = detectForcedTool(userMessage);

  console.log(`  📡 Calling Telnyx Inference (${VOICE_MODEL})...`);
  
  // First LLM call - may return tool_calls
  const response = await fetch(TELNYX_INFERENCE_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TELNYX_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: VOICE_MODEL,
      messages,
      tools,
      tool_choice: toolChoice,
      enable_thinking: false,
    }),
  });

  if (!response.ok) {
    throw new Error(`LLM failed: ${await response.text()}`);
  }

  const data = await response.json();
  const firstTokenTime = Date.now() - requestStart;
  console.log(`  ⚡ Time to response: ${firstTokenTime}ms`);
  console.log(`  🔍 API Response:`, JSON.stringify(data.choices?.[0]?.message, null, 2));
  
  const assistantMessage = data.choices?.[0]?.message;
  if (!assistantMessage) {
    throw new Error('No assistant message in response');
  }

  // Check for tool calls
  if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
    console.log(`  🔧 Tool calls detected: ${assistantMessage.tool_calls.map((t: any) => t.function.name).join(', ')}`);
    
    // Add assistant message to history
    messages.push(assistantMessage);
    
    // Execute each tool
    for (const toolCall of assistantMessage.tool_calls) {
      const fnName = toolCall.function.name;
      const fnArgs = JSON.parse(toolCall.function.arguments || '{}');
      
      // For slow tools (like send_message), give feedback before executing
      if (fnName === 'send_message' && call) {
        const recipient = fnArgs.to || fnArgs.channel || 'that channel';
        queueSpeak(call, `I'll send that message to ${recipient} now, give me a moment.`);
        // Wait briefly for TTS to start
        await new Promise(resolve => setTimeout(resolve, 200));
      }
      
      const result = await executeTool(fnName, fnArgs);
      
      // Add tool result to messages
      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        name: fnName,
        content: result,
      });
    }
    
    // Second LLM call with tool results - STREAM for faster speech
    console.log(`  📡 Second LLM call with tool results (streaming)...`);
    const secondResponse = await fetch(TELNYX_INFERENCE_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${TELNYX_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: VOICE_MODEL,
        messages,
        stream: true,
        enable_thinking: false,
      }),
    });

    if (!secondResponse.ok) {
      throw new Error(`Second LLM call failed: ${await secondResponse.text()}`);
    }

    // Stream and speak sentences as they arrive
    const reader = secondResponse.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let fullResponse = '';
    let buffer = '';
    let sentenceBuffer = '';
    const sentenceEnders = /[.!?]/;
    let firstChunkLogged = false;
    let insideThinkTag = false;
    let thinkBuffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;

          try {
            const json = JSON.parse(data);
            const content = json.choices?.[0]?.delta?.content || '';
            
            if (content) {
              if (!firstChunkLogged) {
                console.log(`  ⚡ Second call first token: ${Date.now() - requestStart}ms`);
                firstChunkLogged = true;
              }
              
              fullResponse += content;
              
              // Handle <think> tags - buffer until we're past them
              if (!insideThinkTag && content.includes('<think>')) {
                insideThinkTag = true;
                thinkBuffer = content;
                continue;
              }
              
              if (insideThinkTag) {
                thinkBuffer += content;
                if (thinkBuffer.includes('</think>')) {
                  // Extract content after </think>
                  const afterThink = thinkBuffer.split('</think>').pop() || '';
                  insideThinkTag = false;
                  thinkBuffer = '';
                  sentenceBuffer += afterThink;
                  console.log(`  🧠 Skipped thinking block`);
                }
                continue;
              }
              
              sentenceBuffer += content;

              // Speak complete sentences as they arrive
              const match = sentenceBuffer.match(sentenceEnders);
              if (match) {
                const idx = sentenceBuffer.search(sentenceEnders) + 1;
                const sentence = sentenceBuffer.slice(0, idx).trim();
                sentenceBuffer = sentenceBuffer.slice(idx);
                
                // Clean and queue for speaking
                const cleanSentence = cleanResponseForSpeech(sentence);
                if (cleanSentence.length > 10) {
                  queueSpeak(call, cleanSentence);
                }
              }
            }
          } catch {
            // Skip malformed JSON
          }
        }
      }
    }

    // Speak any remaining text
    const remaining = cleanResponseForSpeech(sentenceBuffer);
    if (remaining) {
      queueSpeak(call, remaining);
    }
    
    const totalTime = Date.now() - requestStart;
    console.log(`  ✅ Total time (with tools): ${totalTime}ms`);
    
    // Update conversation history
    call.messages.push({ role: 'user', content: userMessage });
    call.messages.push({ role: 'assistant', content: fullResponse });
    
    return fullResponse;
  }
  
  // No tool calls - direct response
  const content = assistantMessage.content || '';
  const totalTime = Date.now() - requestStart;
  console.log(`  ✅ Total time (direct): ${totalTime}ms`);
  
  // Speak the response (non-streaming, so speak full response)
  const cleanContent = cleanResponseForSpeech(content);
  if (cleanContent) {
    queueSpeak(call, cleanContent);
  }
  
  // Update conversation history
  call.messages.push({ role: 'user', content: userMessage });
  call.messages.push({ role: 'assistant', content: content });
  
  // Keep history manageable
  if (call.messages.length > 20) {
    call.messages = call.messages.slice(-20);
  }
  
  return content;
}

async function processTranscript(call: CallState, callControlId: string, transcript: string) {
  console.log(`  🎤 Processing: "${transcript}"`);
  call.isProcessing = true;

  try {
    const lower = transcript.toLowerCase();
    if (lower.includes('bye') || lower.includes('goodbye') || lower.includes('hang up')) {
      queueSpeak(call, "Goodbye! Talk soon!");
      setTimeout(() => callCommand(callControlId, 'hangup'), 2500);
      return;
    }

    const response = await callLLMWithTools(call, transcript);
    console.log(`  🤖 Response: "${response.substring(0, 80)}${response.length > 80 ? '...' : ''}"`);
    
    // NOTE: Don't queue here - streaming already speaks sentences as they arrive
    
  } catch (error) {
    console.error(`  ❌ Error:`, error);
    queueSpeak(call, "Sorry, I had trouble with that. Could you say it again?");
  } finally {
    call.isProcessing = false;
  }
}

// ============================================================================
// WEBHOOK HANDLER
// ============================================================================

app.post('/voice/webhook', async (req, res) => {
  res.status(200).send('OK');

  const event = req.body;
  const eventType = event.data?.event_type;
  const payload = event.data?.payload;
  
  if (!eventType) return;

  const callControlId = payload?.call_control_id;
  console.log(`\n[${new Date().toISOString()}] ${eventType}`);

  try {
    switch (eventType) {
      case 'call.initiated': {
        const { from, to, direction, call_control_id } = payload;
        console.log(`  📞 ${from} → ${to} (${direction})`);
        
        activeCalls.set(call_control_id, {
          callControlId: call_control_id,
          from,
          to,
          messages: [],
          startTime: new Date(),
          isProcessing: false,
          speakQueue: [],
          isSpeaking: false,
          pendingInterrupt: false,
        });

        if (direction === 'incoming') {
          await callCommand(call_control_id, 'answer');
        }
        break;
      }

      case 'call.answered': {
        console.log(`  ✅ Call answered`);
        const call = activeCalls.get(callControlId);
        if (call) call.startTime = new Date();
        
        await callCommand(callControlId, 'transcription_start', {
          language: 'en',
          transcription_engine: 'Telnyx',
          interim_results: true,
        });
        console.log(`  🎙️ Transcription started`);

        await callCommand(callControlId, 'speak', {
          payload: `Hey ${USER_NAME}! What can I help with?`,
          voice: TTS_VOICE,
          language: 'en-GB',
        });
        break;
      }

      case 'call.speak.started': {
        const call = activeCalls.get(callControlId);
        if (call) call.isSpeaking = true;
        break;
      }

      case 'call.speak.ended': {
        console.log(`  🔊 Finished speaking`);
        const call = activeCalls.get(callControlId);
        if (call) {
          call.isSpeaking = false;
          call.pendingInterrupt = false;
          if (call.speakQueue.length > 0) {
            processSpeakQueue(call);
          }
        }
        break;
      }

      case 'call.transcription': {
        const { transcription_data } = payload;
        if (!transcription_data) break;

        const { transcript, is_final } = transcription_data;
        if (!transcript || transcript.trim().length < 2) break;

        const call = activeCalls.get(callControlId);
        if (!call) break;

        console.log(`  📝 Transcript (final=${is_final}): "${transcript.substring(0, 50)}..."`);

        // Barge-in
        if (call.isSpeaking || call.speakQueue.length > 0) {
          await interruptSpeaking(call);
        }

        if (!is_final) break;

        if (call.isProcessing) {
          console.log(`  ⏳ Still processing, queuing...`);
          setTimeout(() => {
            if (!call.isProcessing) {
              processTranscript(call, callControlId, transcript);
            }
          }, 500);
          break;
        }

        await processTranscript(call, callControlId, transcript);
        break;
      }

      case 'call.transcription.stopped': {
        console.log(`  ⚠️ Transcription stopped, restarting...`);
        await callCommand(callControlId, 'transcription_start', {
          language: 'en',
          transcription_engine: 'Telnyx',
          interim_results: true,
        });
        break;
      }

      case 'call.hangup': {
        const { hangup_cause } = payload;
        console.log(`  📴 Hangup: ${hangup_cause}`);
        
        const call = activeCalls.get(callControlId);
        if (call) {
          const duration = (Date.now() - call.startTime.getTime()) / 1000;
          console.log(`  Duration: ${duration.toFixed(1)}s`);
          activeCalls.delete(callControlId);
        }
        break;
      }
    }
  } catch (error) {
    console.error(`  Error:`, error);
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    activeCalls: activeCalls.size, 
    uptime: process.uptime(),
    model: VOICE_MODEL,
    mode: 'function-calling',
    tools: tools.map(t => t.function.name),
  });
});

let tunnelProcess: ChildProcess | undefined;

async function main() {
  console.log('\n🚀 Starting Voice Server (Function Calling Mode)...');
  console.log(`   Model: ${VOICE_MODEL}`);
  console.log(`   Tools: ${tools.map(t => t.function.name).join(', ')}`);
  
  // Load personalization from workspace files
  await loadPersonalization();
  
  // Load gateway config for cross-channel messaging
  await loadGatewayConfig();
  
  VOICE_SYSTEM_PROMPT = buildSystemPrompt(); // Rebuild with loaded values
  console.log();

  await new Promise<void>((resolve) => {
    app.listen(PORT, () => {
      console.log(`🎙️  ${ASSISTANT_NAME} Voice Server ready on port ${PORT}`);
      console.log(`   Mode: Function Calling (Telnyx Inference)`);
      console.log(`   TTS: ${TTS_VOICE}`);
      resolve();
    });
  });

  if (ENABLE_TUNNEL && TELNYX_API_KEY) {
    try {
      // Use assistant name for unique app naming (from IDENTITY.md)
      const safeName = ASSISTANT_NAME.toLowerCase().replace(/[^a-z0-9]/g, '');
      const result = await startTunnel({
        port: PORT,
        telnyxApiKey: TELNYX_API_KEY,
        connectionId: '',
        appName: `${safeName}-voice`,
        sipSubdomain: safeName,
      });
      tunnelProcess = result.process;
      console.log(`\n🎉 Ready!`);
      console.log(`   Webhook: ${result.webhookUrl}`);
      if (result.sipAddress) {
        console.log(`   📞 Dial: ${result.sipAddress}\n`);
      }
    } catch (error) {
      console.error('⚠️ Tunnel failed:', error);
    }
  }
}

process.on('SIGINT', async () => {
  await stopTunnel(tunnelProcess).catch(() => {});
  process.exit(0);
});

main().catch(console.error);
