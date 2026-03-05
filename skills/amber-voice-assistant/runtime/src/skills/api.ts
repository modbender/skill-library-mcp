/**
 * Amber Skills — Constrained API Builder
 * 
 * Builds a SkillCallContext for each handler invocation with permissions
 * enforced based on the skill's manifest.
 */

import { execFileSync } from 'child_process';
import { AmberSkillPermissions, SkillCallContext } from './types.js';
import OpenAI from 'openai';

export interface ApiDependencies {
  /** OpenClaw gateway client (OpenAI-compatible) */
  clawdClient: OpenAI | null;
  /** Operator name from env */
  operatorName: string;
  /** Operator Telegram ID from env (optional) */
  operatorTelegramId?: string;
  /** Current call ID */
  callId: string;
  /** Caller ID (phone number) */
  callerId: string;
  /** Current transcript text */
  transcript: string;
  /** Function to write to the call's JSONL log */
  writeJsonl: (entry: Record<string, any>) => void;
}

/**
 * Build a constrained SkillCallContext based on the skill's declared permissions.
 * The handler can only use capabilities the manifest permits.
 */
export function buildSkillContext(
  permissions: AmberSkillPermissions,
  deps: ApiDependencies
): SkillCallContext {
  const allowedBins = new Set(permissions.local_binaries || []);

  return {
    /**
     * Execute a local binary. Only binaries listed in permissions.local_binaries are allowed.
     *
     * cmd must be a string[] — e.g. ['/usr/local/bin/ical-query', 'today'].
     * Uses execFileSync: no shell is spawned, arguments are passed as discrete tokens,
     * immune to shell injection regardless of argument content.
     */
    exec: async (cmd: string[]): Promise<string> => {
      if (!Array.isArray(cmd) || cmd.length === 0) {
        throw new Error('exec requires a non-empty string[] — shell string commands are not supported');
      }

      const [file, ...args] = cmd;
      const baseBin = file.split('/').pop() || file;

      if (!allowedBins.has(baseBin) && !allowedBins.has(file)) {
        throw new Error(`Permission denied: binary "${baseBin}" not in allowed list [${[...allowedBins].join(', ')}]`);
      }

      try {
        return execFileSync(file, args, { encoding: 'utf8', timeout: 10000 }).trim();
      } catch (e: any) {
        throw new Error(`exec failed: ${e.message || e}`);
      }
    },

    /**
     * Write an entry to the call's JSONL log.
     */
    callLog: {
      write: (entry: Record<string, any>) => {
        deps.writeJsonl({
          ...entry,
          call_id: deps.callId,
          received_at: new Date().toISOString(),
        });
      },
    },

    /**
     * Gateway access — constrained by permissions.
     */
    gateway: {
      /**
       * POST arbitrary payload to OpenClaw gateway. Requires openclaw_action permission.
       */
      post: async (payload: Record<string, any>): Promise<any> => {
        if (!permissions.openclaw_action) {
          throw new Error('Permission denied: openclaw_action not allowed for this skill');
        }
        if (!deps.clawdClient) {
          throw new Error('OpenClaw gateway client not configured');
        }

        const completion = await deps.clawdClient.chat.completions.create({
          model: 'openclaw:main',
          messages: [
            { role: 'system', content: 'You are processing an action request from a voice agent skill. Execute the requested action.' },
            { role: 'user', content: JSON.stringify(payload) },
          ],
          max_tokens: 200,
        });

        return completion.choices?.[0]?.message?.content?.trim() ?? 'Action processed';
      },

      /**
       * Send a message to the operator via OpenClaw gateway. Requires telegram permission.
       * The recipient is always the operator — determined by config, never by caller input.
       */
      sendMessage: async (message: string): Promise<any> => {
        if (!permissions.telegram) {
          throw new Error('Permission denied: telegram messaging not allowed for this skill');
        }
        if (!deps.clawdClient) {
          throw new Error('OpenClaw gateway client not configured');
        }

        // Send via OpenClaw gateway — the gateway routes to the operator's configured channel
        const completion = await deps.clawdClient.chat.completions.create({
          model: 'openclaw:main',
          messages: [
            {
              role: 'system',
              content: [
                'You are processing a message delivery request from a voice agent (Amber).',
                'Send the following message to the operator immediately using the message tool.',
                'The message is from a phone call and should be delivered as-is.',
                'Do not modify the message content. Just deliver it.',
              ].join(' '),
            },
            { role: 'user', content: message },
          ],
          max_tokens: 200,
        });

        return completion.choices?.[0]?.message?.content?.trim() ?? 'Message delivered';
      },
    },

    /**
     * Read-only call context.
     */
    call: {
      id: deps.callId,
      callerId: deps.callerId,
      transcript: deps.transcript,
    },

    /**
     * Operator info from env vars.
     */
    operator: {
      name: deps.operatorName,
      telegramId: deps.operatorTelegramId,
    },
  };
}
