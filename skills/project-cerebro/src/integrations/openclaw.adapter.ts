/**
 * OpenClaw adapter - wraps OpenClaw Gateway API client
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import { logger } from '../lib/logger';
import { OpenClawError } from '../lib/errors';

const execAsync = promisify(exec);

export interface OpenClawAgentConfig {
  agentId: string;
  gatewayUrl: string;
  token: string;
}

export interface OpenClawTaskPayload {
  prompt: string;
  model?: string;
  thinking?: 'low' | 'medium' | 'high';
}

export class OpenClawAdapter {
  constructor(
    private gatewayUrl: string,
    private token: string
  ) {}

  /**
   * Execute a task with an OpenClaw agent
   */
  async executeTask(agentId: string, payload: OpenClawTaskPayload): Promise<string> {
    const command = this.buildCommand(agentId, payload);
    
    logger.info('Executing task with OpenClaw agent', {
      agentId,
      promptLength: payload.prompt.length,
      model: payload.model,
      thinking: payload.thinking,
      command: command.substring(0, 200) + (command.length > 200 ? '...' : ''), // Log truncated command for debugging
    });

    try {
      const { stdout, stderr } = await execAsync(command, {
        timeout: 600000, // 10 minute timeout
        maxBuffer: 10 * 1024 * 1024, // 10MB buffer for large responses
      });

      if (stderr) {
        logger.warn('OpenClaw execution stderr output', { 
          agentId,
          stderr: stderr.substring(0, 500),
        });
      }

      logger.info('OpenClaw task completed successfully', {
        agentId,
        outputLength: stdout.length,
        outputPreview: stdout.substring(0, 200),
      });

      // If using --json, parse the response and extract agent-visible text.
      // NOTE: OpenClaw's --json output contains a lot of meta (run reports, usage, etc.).
      // We only want actual agent replies (payload text). If there is no payload text,
      // return a short diagnostic instead of dumping the full JSON into reports.
      try {
        const jsonResponse = JSON.parse(stdout);

        // 1) Prefer agent reply payloads
        const payloads = jsonResponse.result?.payloads;
        if (payloads && Array.isArray(payloads)) {
          const texts = payloads
            .map((p: any) => p.text?.trim())
            .filter((t: string | null) => t && t.length > 0);

          // Deduplicate texts (agent sometimes sends same content multiple times)
          const uniqueTexts: string[] = [];
          for (const text of texts) {
            const isDuplicate = uniqueTexts.some((seen) => seen.includes(text) || text.includes(seen));
            if (!isDuplicate) uniqueTexts.push(text);
          }

          if (uniqueTexts.length > 0) {
            return uniqueTexts.join('\n\n');
          }
        }

        // 2) If the gateway reported an error, surface it
        const errorLike =
          jsonResponse.error ||
          jsonResponse.result?.error ||
          jsonResponse.result?.message ||
          jsonResponse.message;

        const errorText = typeof errorLike === 'string' ? errorLike : undefined;
        if (errorText && /no models match|model restrictions|404/i.test(errorText)) {
          return `ERROR: ${errorText}`;
        }

        // 3) Otherwise, avoid dumping massive meta JSON into the report
        const summary =
          (typeof jsonResponse.result?.summary === 'string' && jsonResponse.result.summary) ||
          (typeof jsonResponse.summary === 'string' && jsonResponse.summary) ||
          (typeof jsonResponse.result?.status === 'string' && jsonResponse.result.status) ||
          (typeof jsonResponse.status === 'string' && jsonResponse.status);

        if (summary) {
          return `(no agent output) ${summary}`;
        }

        return '(no agent output)';
      } catch {
        // Not JSON, return raw output
        return stdout;
      }
    } catch (error: any) {
      // Capture detailed error information
      const errorDetails = {
        agentId,
        promptLength: payload.prompt.length,
        exitCode: error.code,
        signal: error.signal,
        killed: error.killed,
        stdout: error.stdout?.substring(0, 1000) || '',
        stderr: error.stderr?.substring(0, 1000) || '',
        message: error.message,
        command: command.substring(0, 100) + '...',
      };
      
      logger.error('OpenClaw task execution failed', error as Error, errorDetails);
      
      // Include more context in the thrown error
      const detailedMessage = `OpenClaw task execution failed for agent "${agentId}": ${error.message || 'Unknown error'}. ` +
        `Exit code: ${error.code || 'N/A'}. ` +
        `Stderr: ${error.stderr?.substring(0, 200) || 'None'}`;
      
      throw new OpenClawError(detailedMessage);
    }
  }

  /**
   * Build the openclaw CLI command
   * 
   * OpenClaw CLI usage:
   *   openclaw agent --agent <id> --message <text> [--thinking <level>] [--json]
   * 
   * Note: --gateway and --token are not CLI flags; they're configured via
   * OpenClaw config or environment variables.
   * 
   * We use the full path to openclaw because the PATH may not be set correctly
   * when running from a systemd service or backgrounded node process.
   */
  private buildCommand(agentId: string, payload: OpenClawTaskPayload): string {
    // Use full path to openclaw CLI to ensure it's found regardless of PATH
    const openclawPath = process.env.OPENCLAW_CLI_PATH || 'openclaw';
    const parts: string[] = [openclawPath, 'agent'];
    
    parts.push('--agent', agentId);
    
    if (payload.thinking) {
      parts.push('--thinking', payload.thinking);
    }
    
    // Use --json for structured output that's easier to parse
    parts.push('--json');
    
    // Escape the message for shell. The message goes via --message (not --prompt).
    // Use single quotes and escape any single quotes in the content.
    const escapedMessage = payload.prompt.replace(/'/g, "'\\''");
    parts.push('--message', `'${escapedMessage}'`);

    return parts.join(' ');
  }

  /**
   * Send a message via OpenClaw CLI
   */
  async sendMessage(to: string, message: string, channelType: string = 'discord'): Promise<void> {
    const openclawPath = process.env.OPENCLAW_CLI_PATH || 'openclaw';
    const parts: string[] = [openclawPath, 'message', 'send'];
    
    // Target channel or user - strip 'channel:' prefix if present
    const target = to.replace(/^channel:/, '');
    parts.push('--target', target);
    
    // Channel type (discord, telegram, etc.)
    parts.push('--channel', channelType);
    
    // Message content (escaped)
    const escapedMessage = message.replace(/'/g, "'\\''");
    parts.push('--message', `'${escapedMessage}'`);

    const command = parts.join(' ');

    logger.debug('Sending message via OpenClaw', { to: target, channel: channelType, command: command.substring(0, 100) + '...' });

    try {
      const { stdout, stderr } = await execAsync(command);
      logger.info('Message sent via OpenClaw', { to: target, channel: channelType, stdout: stdout?.substring(0, 200), stderr: stderr?.substring(0, 200) });
    } catch (error: any) {
      logger.error('Failed to send message via OpenClaw', error as Error, { 
        to: target, 
        channel: channelType,
        stdout: error.stdout?.substring(0, 500),
        stderr: error.stderr?.substring(0, 500),
        code: error.code 
      });
      throw new OpenClawError(`Failed to send message: ${error.message}. stderr: ${error.stderr?.substring(0, 200)}`);
    }
  }

  /**
   * Get schedule context (calls get-schedule.js script)
   */
  async getScheduleContext(): Promise<string> {
    try {
      const scriptPath = path.join(process.cwd(), 'dist', 'scripts', 'get-schedule.js');
      const { stdout } = await execAsync(`node ${scriptPath}`);
      logger.debug('Schedule context retrieved', {
        outputLength: stdout.length,
      });
      return stdout;
    } catch (error) {
      logger.error('Failed to get schedule context', error as Error);
      return '';
    }
  }
}
