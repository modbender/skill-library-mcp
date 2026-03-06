// @elvatis/openclaw-rss-feeds - Channel notifier via openclaw CLI subprocess
import { execFileSync } from 'child_process';

/**
 * Parse a notification target string in format "channel:target"
 * Examples:
 *   "whatsapp:+49xxxxxxxxxx"
 *   "telegram:123456789"
 *   "discord:#general"
 */
interface ParsedTarget {
  channel: string;
  target: string;
}

function parseTarget(raw: string): ParsedTarget | null {
  const colonIdx = raw.indexOf(':');
  if (colonIdx === -1) {
    console.warn(`[notifier] Invalid target format (expected "channel:target"): ${raw}`);
    return null;
  }
  return {
    channel: raw.substring(0, colonIdx).trim(),
    target: raw.substring(colonIdx + 1).trim(),
  };
}

/**
 * Send a notification to one or more targets via the openclaw CLI.
 * Uses execFileSync (no shell) to prevent shell injection.
 *
 * @param targets - Array of "channel:target" strings
 * @param message - Message text to send
 */
export async function notify(targets: string[], message: string): Promise<void> {
  if (!targets || targets.length === 0) return;

  for (const raw of targets) {
    const parsed = parseTarget(raw);
    if (!parsed) continue;

    try {
      execFileSync('openclaw', [
        'message',
        'send',
        '--channel',
        parsed.channel,
        '--target',
        parsed.target,
        '--message',
        message,
      ], {
        timeout: 30000,
        stdio: 'pipe',
      });

      console.info(`[notifier] Notification sent to ${raw}`);
    } catch (err) {
      // Non-fatal: log and continue to next target
      const errMsg = err instanceof Error ? err.message : String(err);
      console.warn(`[notifier] Failed to notify ${raw}: ${errMsg}`);
    }
  }
}

/**
 * Build a standard digest notification message.
 */
export function buildDigestNotification(params: {
  title: string;
  firmwareCount: number;
  cveCount: number;
  ghostUrl?: string;
  ghostError?: string;
  period: string;
}): string {
  const { title, firmwareCount, cveCount, ghostUrl, ghostError, period } = params;

  let msg = `📋 Digest ready: ${title}\n\n`;
  msg += `📅 Period: ${period}\n`;
  msg += `📦 Firmware updates: ${firmwareCount}\n`;
  msg += `⚠️ CVEs (above threshold): ${cveCount}\n`;

  if (ghostUrl) {
    msg += `\n✅ Draft published: ${ghostUrl}`;
  } else if (ghostError) {
    msg += `\n❌ Ghost publish failed: ${ghostError}`;
  }

  return msg;
}
