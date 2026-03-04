/**
 * Amber Voice Agent — MCP Server
 *
 * Exposes Amber's telephony and skill capabilities as MCP tools for
 * Claude Cowork. This is a thin adapter layer — the actual logic lives
 * in the existing bridge (index.ts) and skill handlers.
 *
 * Architecture:
 *   Claude Cowork ←→ MCP (stdio/JSON-RPC) ←→ this file ←→ bridge HTTP API
 *
 * The bridge must be running (npm start) for telephony tools to work.
 * Calendar and CRM tools call the skill handlers directly (no bridge needed).
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

// ─── Configuration ───

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BRIDGE_URL = process.env.AMBER_BRIDGE_URL ?? 'http://127.0.0.1:8000';
const BRIDGE_API_TOKEN = process.env.BRIDGE_API_TOKEN ?? '';
const OPERATOR_NAME = process.env.OPERATOR_NAME ?? '';
const LOGS_DIR = process.env.AMBER_LOGS_DIR ?? path.join(__dirname, '..', 'logs');

// ─── Helpers ───

async function bridgeRequest(endpoint: string, body: Record<string, any>): Promise<any> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (BRIDGE_API_TOKEN) {
    headers['Authorization'] = `Bearer ${BRIDGE_API_TOKEN}`;
  }

  const res = await fetch(`${BRIDGE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Bridge ${endpoint} failed (${res.status}): ${text}`);
  }

  return res.json();
}

/**
 * Load and execute a skill handler directly (for calendar, CRM).
 * These don't need the bridge running — they use local binaries/files.
 */
async function executeSkillHandler(
  skillName: string,
  params: Record<string, any>
): Promise<{ success: boolean; message?: string; result?: any; error?: string }> {
  const handlerPath = path.join(__dirname, '..', '..', 'amber-skills', skillName, 'handler.js');

  if (!fs.existsSync(handlerPath)) {
    return { success: false, error: `Skill handler not found: ${skillName}` };
  }

  // Dynamic import of the CJS handler
  const mod = await import(handlerPath);
  const handler = mod.default ?? mod;

  // Build a minimal skill context (no call-specific deps needed for MCP usage)
  const context = buildMcpSkillContext();

  return handler(params, context);
}

/**
 * Build a minimal SkillCallContext for MCP-driven skill calls.
 * No active call, no WebSocket — just the exec and logging capabilities.
 */
function buildMcpSkillContext() {
  const allowedBins = new Set(['/usr/local/bin/ical-query']);

  return {
    exec: async (cmd: string[]): Promise<string> => {
      if (!Array.isArray(cmd) || cmd.length === 0) {
        throw new Error('exec requires a non-empty string[]');
      }
      const [file, ...args] = cmd;
      const baseBin = file.split('/').pop() || file;
      if (!allowedBins.has(baseBin) && !allowedBins.has(file)) {
        throw new Error(`Permission denied: binary "${baseBin}" not allowed`);
      }
      const { execFileSync } = await import('node:child_process');
      return execFileSync(file, args, { encoding: 'utf8', timeout: 10000 }).trim();
    },

    callLog: {
      write: (_entry: Record<string, any>) => {
        // No-op for MCP context — no active call log
      },
    },

    gateway: {
      post: async (_payload: Record<string, any>) => {
        throw new Error('Gateway actions not available in MCP mode');
      },
      sendMessage: async (_message: string) => {
        throw new Error('Gateway messaging not available in MCP mode');
      },
    },

    call: {
      id: 'mcp-session',
      callerId: '',
      transcript: '',
    },

    operator: {
      name: OPERATOR_NAME,
      telegramId: undefined,
    },
  };
}

/**
 * Read call logs from the logs directory and return structured history.
 */
function getCallHistory(filter: string = 'all', limit: number = 10): any[] {
  if (!fs.existsSync(LOGS_DIR)) return [];

  const files = fs.readdirSync(LOGS_DIR)
    .filter(f => f.endsWith('.summary.json'))
    .sort()
    .reverse()
    .slice(0, limit * 2); // over-read since we filter

  const calls: any[] = [];
  for (const file of files) {
    try {
      const summary = JSON.parse(fs.readFileSync(path.join(LOGS_DIR, file), 'utf8'));

      // Apply filter
      if (filter !== 'all') {
        const direction = summary.direction ?? 'unknown';
        if (filter === 'inbound' && direction !== 'inbound') continue;
        if (filter === 'outbound' && direction !== 'outbound') continue;
        if (filter === 'missed' && summary.status !== 'missed') continue;
      }

      // Try to load transcript
      const callId = file.replace('.summary.json', '');
      const transcriptPath = path.join(LOGS_DIR, `${callId}.txt`);
      const transcript = fs.existsSync(transcriptPath)
        ? fs.readFileSync(transcriptPath, 'utf8').trim()
        : null;

      calls.push({
        callId,
        ...summary,
        transcript,
      });

      if (calls.length >= limit) break;
    } catch {
      // Skip malformed files
    }
  }

  return calls;
}

// ─── MCP Server ───

const server = new Server(
  {
    name: 'amber-voice-agent',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// ─── Tool Definitions ───

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'make_call',
      description:
        'Make an outbound phone call via Twilio. Amber will handle the conversation ' +
        'autonomously, pursuing the stated objective. ALWAYS use contacts_lookup first ' +
        'to resolve a name to a verified phone number. The tool will show who it is about ' +
        'to call and require confirmed=true before actually dialing — this prevents wrong-number calls.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          to: {
            type: 'string',
            description: 'Phone number in E.164 format. Optional if name is provided.',
          },
          name: {
            type: 'string',
            description: 'Contact name to call (e.g., "Abe"). Will be resolved to a phone number via Apple Contacts. Use this instead of to when possible.',
          },
          objective: {
            type: 'string',
            description: 'What to accomplish on the call (e.g., "book a table for 4 at 7pm")',
          },
          confirmed: {
            type: 'boolean',
            description: 'Set to true only after the tool has shown you who it will call and you have verified the number. Never set this on the first attempt.',
          },
        },
        required: ['objective'],
      },
    },
    {
      name: 'get_call_status',
      description: 'Check the status and transcript of an active or recent call.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          callId: {
            type: 'string',
            description: 'The call ID returned by make_call',
          },
        },
        required: ['callId'],
      },
    },
    {
      name: 'get_call_history',
      description: 'Retrieve recent call logs with transcripts and AI summaries.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          filter: {
            type: 'string',
            enum: ['all', 'inbound', 'outbound', 'missed'],
            description: 'Filter by call direction (default: all)',
          },
          limit: {
            type: 'number',
            description: 'Number of calls to return (default: 10)',
          },
        },
      },
    },
    {
      name: 'start_screening',
      description:
        'Enable inbound call screening. Amber will answer incoming calls, ' +
        'identify the caller, take a message, and deliver a structured summary.',
      inputSchema: {
        type: 'object' as const,
        properties: {},
      },
    },
    {
      name: 'stop_screening',
      description: 'Disable inbound call screening. Calls will ring through normally.',
      inputSchema: {
        type: 'object' as const,
        properties: {},
      },
    },
    {
      name: 'calendar_query',
      description:
        'Check calendar availability or create events. For lookups, returns ' +
        'busy time slots (event titles are private). For creation, adds an event.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          action: {
            type: 'string',
            enum: ['lookup', 'create'],
            description: '"lookup" to check availability, "create" to add an event',
          },
          range: {
            type: 'string',
            description: 'For lookup: "today", "tomorrow", "week", or a date (YYYY-MM-DD)',
          },
          title: {
            type: 'string',
            description: 'For create: event title',
          },
          start: {
            type: 'string',
            description: 'For create: start time (YYYY-MM-DDTHH:MM)',
          },
          end: {
            type: 'string',
            description: 'For create: end time (YYYY-MM-DDTHH:MM)',
          },
          calendar: {
            type: 'string',
            description: 'Calendar name (optional, defaults to primary)',
          },
          location: {
            type: 'string',
            description: 'For create: event location (optional)',
          },
          notes: {
            type: 'string',
            description: 'For create: event notes (optional)',
          },
        },
        required: ['action'],
      },
    },
    {
      name: 'crm',
      description:
        'Manage contacts and interaction history. Look up contacts by phone or name, ' +
        'create new contacts, update existing ones, or view interaction history.',
      inputSchema: {
        type: 'object' as const,
        properties: {
          action: {
            type: 'string',
            enum: ['lookup', 'create', 'update', 'log', 'history'],
            description: 'CRM action to perform',
          },
          identifier: {
            type: 'string',
            description: 'Phone number or name to look up (for lookup/history actions)',
          },
          phone: {
            type: 'string',
            description: 'Phone number (used for history, log, create, update actions)',
          },
          name: {
            type: 'string',
            description: 'Contact name',
          },
          email: {
            type: 'string',
            description: 'Email address',
          },
          notes: {
            type: 'string',
            description: 'Notes about the contact or interaction',
          },
          tags: {
            type: 'array',
            items: { type: 'string' },
            description: 'Tags for categorization',
          },
        },
        required: ['action'],
      },
    },
    {
      name: 'bridge_health',
      description:
        'Check if the Amber voice bridge is running and healthy. ' +
        'The bridge must be running for telephony features (calls, screening) to work.',
      inputSchema: {
        type: 'object' as const,
        properties: {},
      },
    },
    {
      name: 'contacts_lookup',
      description:
        'Search Apple Contacts by name or phone number. Use this to find someone\'s ' +
        'phone number before making a call (e.g., "find my mother\'s number").',
      inputSchema: {
        type: 'object' as const,
        properties: {
          name: {
            type: 'string',
            description: 'Contact name to search for (fuzzy, case-insensitive)',
          },
          phone: {
            type: 'string',
            description: 'Phone number to look up (find who it belongs to)',
          },
        },
      },
    },
  ],
}));

// ─── Tool Handlers ───

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'make_call': {
        let { to, name: toName, objective, confirmed } = args as { to?: string; name?: string; objective: string; confirmed?: boolean };

        // Resolve name → phone number via contacts cache
        if (!to && toName) {
          const cachePath = path.join(__dirname, '..', 'contacts-cache.json');
          if (!fs.existsSync(cachePath)) {
            return { content: [{ type: 'text', text: 'Contacts cache not found. Run `npm run sync-contacts` first.' }], isError: true };
          }
          const cache = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
          const contacts: any[] = cache.contacts || [];
          const q = toName.toLowerCase();
          const matches = contacts.filter((c: any) =>
            `${c.firstName} ${c.lastName}`.toLowerCase().includes(q) ||
            c.firstName?.toLowerCase().includes(q) ||
            c.lastName?.toLowerCase().includes(q) ||
            c.nickname?.toLowerCase().includes(q)
          ).filter((c: any) => c.phones?.length > 0 || c.phone);

          if (matches.length === 0) {
            return { content: [{ type: 'text', text: `No contact found named "${toName}" with a phone number.` }], isError: true };
          }
          if (matches.length > 1) {
            const names = matches.map((c: any) => `${c.firstName} ${c.lastName}`.trim() + ` (${(c.phones?.[0]?.number || c.phone)})`).join('\n');
            return { content: [{ type: 'text', text: `Multiple contacts matched "${toName}":\n${names}\n\nBe more specific or pass the phone number directly.` }], isError: true };
          }
          const contact = matches[0];
          to = contact.phones?.[0]?.number || contact.phone;
          toName = [contact.firstName, contact.lastName].filter(Boolean).join(' ');
        }

        if (!to || !/^\+?\d[\d\s\-().]{6,}$/.test(to)) {
          return {
            content: [{ type: 'text', text: 'Invalid or missing phone number. Provide a name (name=) or E.164 number (to=).' }],
            isError: true,
          };
        }

        // Normalize to E.164 (strip formatting)
        to = '+' + to.replace(/\D/g, '');

        // Safety check: always verify number against contacts cache before dialing.
        // Require explicit confirmed=true if no matching contact is found.
        if (!confirmed) {
          const cachePath = path.join(__dirname, '..', 'contacts-cache.json');
          let matchedName: string | null = null;
          if (fs.existsSync(cachePath)) {
            try {
              const cache = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
              const contacts: any[] = cache.contacts || [];
              const digits = to.replace(/\D/g, '').slice(-10);
              const match = contacts.find((c: any) => {
                const phones: any[] = c.phones || (c.phone ? [{ number: c.phone }] : []);
                return phones.some((p: any) => (p.number || '').replace(/\D/g, '').slice(-10) === digits);
              });
              if (match) {
                matchedName = [match.firstName, match.lastName].filter(Boolean).join(' ') || match.organization || null;
              }
            } catch {}
          }

          if (!matchedName) {
            return {
              content: [{
                type: 'text',
                text: `⚠️ Safety check: "${to}" was not found in Apple Contacts. Cannot verify this number belongs to the intended person.\n\nTo proceed anyway, call again with confirmed=true. To find the correct number first, use contacts_lookup.`,
              }],
              isError: true,
            };
          }

          // Found in contacts — show who we're about to call and require one more confirmation step
          return {
            content: [{
              type: 'text',
              text: `📞 About to call **${matchedName}** at ${to}.\nObjective: ${objective}\n\nTo confirm and place the call, call make_call again with confirmed=true.`,
            }],
          };
        }

        const result = await bridgeRequest('/call/outbound', { to, objective });
        return {
          content: [{
            type: 'text',
            text: `Call initiated.\n- Call SID: ${result.sid}\n- Status: ${result.status}\n- To: ${to}\n- Objective: ${objective}\n\nAmber is handling the call. Use get_call_status with the Call SID to check progress.`,
          }],
        };
      }

      case 'get_call_status': {
        const { callId } = args as { callId: string };
        const safeId = callId.replace(/[^a-zA-Z0-9._-]/g, '_');

        // Check for summary
        const summaryPath = path.join(LOGS_DIR, `${safeId}.summary.json`);
        const transcriptPath = path.join(LOGS_DIR, `${safeId}.txt`);

        const parts: string[] = [`Call ID: ${callId}`];

        if (fs.existsSync(summaryPath)) {
          const summary = JSON.parse(fs.readFileSync(summaryPath, 'utf8'));
          parts.push(`Status: ${summary.status ?? 'completed'}`);
          parts.push(`Direction: ${summary.direction ?? 'unknown'}`);
          if (summary.summary) parts.push(`Summary: ${summary.summary}`);
          if (summary.duration) parts.push(`Duration: ${summary.duration}s`);
        } else {
          parts.push('Status: in progress or not found');
        }

        if (fs.existsSync(transcriptPath)) {
          const transcript = fs.readFileSync(transcriptPath, 'utf8').trim();
          if (transcript) parts.push(`\nTranscript:\n${transcript}`);
        }

        return { content: [{ type: 'text', text: parts.join('\n') }] };
      }

      case 'get_call_history': {
        const filter = (args as any)?.filter ?? 'all';
        const limit = (args as any)?.limit ?? 10;
        const calls = getCallHistory(filter, limit);

        if (calls.length === 0) {
          return { content: [{ type: 'text', text: 'No calls found.' }] };
        }

        const formatted = calls.map((c, i) => {
          const lines = [
            `### Call ${i + 1}`,
            `- Direction: ${c.direction ?? 'unknown'}`,
            `- Phone: ${c.caller ?? c.to ?? 'unknown'}`,
            `- Date: ${c.date ?? c.timestamp ?? 'unknown'}`,
            `- Duration: ${c.duration ?? 'unknown'}`,
          ];
          if (c.summary) lines.push(`- Summary: ${c.summary}`);
          if (c.transcript) lines.push(`- Transcript: ${c.transcript.slice(0, 500)}${c.transcript.length > 500 ? '...' : ''}`);
          return lines.join('\n');
        });

        return { content: [{ type: 'text', text: formatted.join('\n\n') }] };
      }

      case 'start_screening': {
        // The bridge handles screening automatically when running.
        // This is a status confirmation — use GET /healthz directly.
        try {
          const res = await fetch(`${BRIDGE_URL}/healthz`);
          const data = await res.json();
          if (!data.ok) throw new Error('unhealthy');
          return {
            content: [{
              type: 'text',
              text: 'Call screening is active. Amber is answering incoming calls on your Twilio number. Summaries will appear in your call history.',
            }],
          };
        } catch {
          return {
            content: [{
              type: 'text',
              text: 'The Amber bridge is not running. Start it with `npm start` in the runtime directory, then screening will activate automatically.',
            }],
            isError: true,
          };
        }
      }

      case 'stop_screening': {
        return {
          content: [{
            type: 'text',
            text: 'To stop screening, shut down the Amber bridge process. While the bridge is running, it automatically answers inbound calls.',
          }],
        };
      }

      case 'calendar_query': {
        const result = await executeSkillHandler('calendar', args as Record<string, any>);
        return {
          content: [{
            type: 'text',
            text: result.message ?? JSON.stringify(result.result ?? result),
          }],
          isError: !result.success,
        };
      }

      case 'crm': {
        // Format CRM results into readable text
        const formatCrmResult = (result: any): string => {
          if (!result.success) return result.message ?? result.error ?? JSON.stringify(result);
          if (!result.result) return result.message ?? 'No results.';
          const items = Array.isArray(result.result) ? result.result : [result.result];
          if (items.length === 0) return result.message ?? 'No results found.';

          // Detect if these are interaction records (have direction/summary fields)
          const isInteractions = items[0] && ('direction' in items[0] || 'summary' in items[0] || 'outcome' in items[0]);

          if (isInteractions) {
            const header = result.message ? `${result.message}\n\n` : '';
            return header + items.map((i: any, idx: number) => {
              const lines = [`**Interaction ${idx + 1}**`];
              if (i.direction) lines.push(`Direction: ${i.direction}`);
              if (i.summary) lines.push(`Summary: ${i.summary}`);
              if (i.outcome) lines.push(`Outcome: ${i.outcome}`);
              if (i.created_at) lines.push(`Date: ${i.created_at}`);
              if (i.details) {
                try {
                  const d = typeof i.details === 'string' ? JSON.parse(i.details) : i.details;
                  if (d.notes) lines.push(`Notes: ${d.notes}`);
                } catch {}
              }
              return lines.join('\n');
            }).join('\n\n');
          }

          // Contact records
          return items.map((c: any) => {
            const lines = [`### ${c.name || 'Unknown'}`];
            if (c.phone) lines.push(`📱 ${c.phone}`);
            if (c.email) lines.push(`📧 ${c.email}`);
            if (c.company) lines.push(`🏢 ${c.company}`);
            if (c.context_notes) lines.push(`📝 ${c.context_notes}`);
            if (c.tags?.length) lines.push(`🏷️ ${c.tags.join(', ')}`);
            if (c.source) lines.push(`Source: ${c.source}`);
            if (c.created_at) lines.push(`Created: ${c.created_at}`);
            return lines.join('\n');
          }).join('\n\n');
        };
        // Map MCP-friendly action names to handler's internal action names
        const crmActionMap: Record<string, string> = {
          lookup:  'search_contacts',   // fuzzy search by name/phone
          create:  'upsert_contact',
          update:  'upsert_contact',
          log:     'log_interaction',
          history: 'get_history',
          search:  'search_contacts',
          tag:     'tag_contact',
        };
        const rawArgs = args as Record<string, any>;
        if (rawArgs.action && crmActionMap[rawArgs.action]) {
          rawArgs.action = crmActionMap[rawArgs.action];
        }
        // search_contacts uses 'query' not 'identifier'
        if (rawArgs.action === 'search_contacts' && rawArgs.identifier && !rawArgs.query) {
          rawArgs.query = rawArgs.identifier;
        }
        // get_history uses 'phone' not 'identifier'
        if (rawArgs.action === 'get_history' && rawArgs.identifier && !rawArgs.phone) {
          rawArgs.phone = rawArgs.identifier;
        }
        const result = await executeSkillHandler('crm', rawArgs);
        return {
          content: [{ type: 'text', text: formatCrmResult(result) }],
          isError: !result.success,
        };
      }

      case 'contacts_lookup': {
        const contactName = (args as any)?.name;
        const contactPhone = (args as any)?.phone;

        if (!contactName && !contactPhone) {
          return {
            content: [{ type: 'text', text: 'Provide either a name or phone number to search.' }],
            isError: true,
          };
        }

        try {
          // Read from pre-exported contacts cache (JSON file in runtime dir).
          // The cache is generated by `npm run sync-contacts` which runs from
          // a context with full AddressBook access (Terminal/setup wizard).
          // This avoids all macOS TCC permission issues.
          const cachePath = path.join(__dirname, '..', 'contacts-cache.json');

          if (!fs.existsSync(cachePath)) {
            return {
              content: [{
                type: 'text',
                text: 'Contacts cache not found. Run `npm run sync-contacts` from Terminal to export your Apple Contacts.',
              }],
              isError: true,
            };
          }

          const cache = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
          const contacts: any[] = cache.contacts || [];

          let matches: any[];
          if (contactName) {
            const q = contactName.toLowerCase();
            matches = contacts.filter((c: any) => {
              const full = `${c.firstName} ${c.lastName}`.toLowerCase();
              return c.firstName?.toLowerCase().includes(q)
                || c.lastName?.toLowerCase().includes(q)
                || full.includes(q)
                || c.nickname?.toLowerCase().includes(q)
                || c.organization?.toLowerCase().includes(q);
            });
          } else {
            const digits = contactPhone!.replace(/\D/g, '').slice(-10);
            matches = contacts.filter((c: any) => {
              const phoneDigits = (c.phone || '').replace(/\D/g, '').slice(-10);
              return phoneDigits === digits;
            });
          }

          if (matches.length === 0) {
            return {
              content: [{
                type: 'text',
                text: `No contacts found for "${contactName || contactPhone}".`,
              }],
            };
          }

          const formatted = matches.map((c: any) => {
            const fullName = [c.firstName, c.lastName].filter(Boolean).join(' ') || c.organization || 'Unknown';
            const lines = [`### ${fullName}`];
            if (c.organization) lines.push(`🏢 ${c.organization}${c.jobTitle ? ` — ${c.jobTitle}` : ''}`);
            if (c.phones?.length) {
              lines.push(`📱 ${c.phones.map((p: any) => `${p.number}${p.label ? ` (${p.label})` : ''}`).join(', ')}`);
            }
            if (c.emails?.length) {
              lines.push(`📧 ${c.emails.map((e: any) => `${e.address}${e.label ? ` (${e.label})` : ''}`).join(', ')}`);
            }
            if (c.relationships?.length) {
              lines.push(`👥 ${c.relationships.map((r: any) => `${r.name} (${r.type})`).join(', ')}`);
            }
            if (c.addresses?.length) {
              lines.push(`📍 ${c.addresses[0].full}`);
            }
            if (c.note) lines.push(`📝 ${c.note}`);
            return lines.join('\n');
          }).join('\n\n');

          const age = cache.exportedAt
            ? `\n\n_Cache last updated: ${new Date(cache.exportedAt).toLocaleString()}_`
            : '';

          return {
            content: [{
              type: 'text',
              text: `Found ${matches.length} result(s):\n${formatted}${age}`,
            }],
          };
        } catch (e: any) {
          return {
            content: [{
              type: 'text',
              text: `Error looking up contacts: ${e.message ?? String(e)}`,
            }],
            isError: true,
          };
        }
      }

      case 'bridge_health': {
        try {
          const res = await fetch(`${BRIDGE_URL}/healthz`);
          const data = await res.json();
          return {
            content: [{
              type: 'text',
              text: data.ok
                ? 'Amber bridge is running and healthy. Telephony features are available.'
                : 'Amber bridge responded but reported unhealthy status.',
            }],
          };
        } catch (e: any) {
          return {
            content: [{
              type: 'text',
              text: `Amber bridge is not reachable at ${BRIDGE_URL}. Telephony features (calls, screening) are unavailable. Calendar and CRM still work. Start the bridge with \`npm start\` in the runtime directory.`,
            }],
            isError: true,
          };
        }
      }

      default:
        return {
          content: [{ type: 'text', text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (e: any) {
    return {
      content: [{ type: 'text', text: `Error: ${e.message ?? String(e)}` }],
      isError: true,
    };
  }
});

// ─── Start ───

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('[amber-mcp] MCP server running on stdio');
}

main().catch((e) => {
  console.error('[amber-mcp] Fatal:', e);
  process.exit(1);
});
