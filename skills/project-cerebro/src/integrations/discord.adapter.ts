/**
 * Discord adapter - wraps Discord client for cleaner interface.
 * CURRENTLY DISABLED - ALL MESSAGES ARE ROUTED VIA OPENCLAW ADAPTER.
 */

import { logger } from '../lib/logger';
import { DiscordError } from '../lib/errors';
import { OpenClawAdapter } from './openclaw.adapter'; // Import OpenClawAdapter

export class DiscordAdapter {
  // We no longer manage a direct Discord client.
  // Instead, we'll use the OpenClawAdapter to send messages.
  private openClawAdapter: OpenClawAdapter;

  constructor(token: string, openClawAdapter: OpenClawAdapter) {
    // Inject OpenClawAdapter
    this.openClawAdapter = openClawAdapter;
    logger.warn('DiscordAdapter initialized but is DISABLED for direct Discord connections. All messages will be routed via OpenClawAdapter.');
  }

  /**
   * Connect to Discord - Disabled, connections are now handled by OpenClaw Gateway.
   */
  async connect(): Promise<void> {
    logger.warn('DiscordAdapter.connect() called, but direct Discord connections are disabled. No action taken.');
    // throw new DiscordError('Direct Discord connections are disabled. Use OpenClaw Gateway.');
  }

  /**
   * Disconnect from Discord - Disabled.
   */
  async disconnect(): Promise<void> {
    logger.warn('DiscordAdapter.disconnect() called, but direct Discord connections are disabled. No action taken.');
  }

  /**
   * Send a message to a channel - now routed via OpenClawAdapter.
   */
  async sendMessage(channelId: string, content: string): Promise<void> {
    try {
      await this.openClawAdapter.sendMessage(`channel:${channelId}`, content);
      logger.debug('Message sent via OpenClaw Discord integration', {
        channelId,
        contentLength: content.length,
      });
    } catch (error) {
      logger.error('Failed to send message via OpenClaw Discord integration', error as Error, { channelId });
      throw new DiscordError('Failed to send message via OpenClaw Discord integration');
    }
  }

  /**
   * Register a message handler for a specific channel - Disabled.
   * Incoming messages are now handled by OpenClaw Gateway.
   */
  onMessage(channelId: string, handler: (message: string) => void | Promise<void>): void {
    logger.warn('DiscordAdapter.onMessage() called, but direct Discord message handling is disabled. No action taken.');
    // If you need to handle incoming messages, configure OpenClaw Gateway to
    // route them to the appropriate Cerebro endpoint or Brain.
  }

  // Dummy methods for compatibility if needed elsewhere
  getClient(): any {
    logger.warn('DiscordAdapter.getClient() called, but direct Discord client is disabled. Returning null.');
    return null;
  }

  isReady(): boolean {
    return true; // We're always "ready" if OpenClaw is.
  }
}
