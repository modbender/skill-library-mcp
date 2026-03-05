/**
 * Context brain - handles context/knowledge management for a specific domain
 */

import { BaseBrain } from '../base-brain';
import { TaskStatus } from '../../domain/types';
import { ReportService } from '../../services';
import * as fs from 'fs';
import * as path from 'path';

export class ContextBrain extends BaseBrain {
  private reportService: ReportService;
  private storagePath: string;

  constructor(
    config: any,
    taskRepo: any,
    discordAdapter: any,
    openClawAdapter: any,
    taskExecutor: any
  ) {
    super(config, taskRepo, discordAdapter, openClawAdapter, taskExecutor);
    this.reportService = new ReportService();
    this.storagePath = path.join(process.cwd(), 'data', this.id);
    this.ensureStorage();
  }

  /**
   * Ensure storage directories exist
   */
  private ensureStorage(): void {
    if (!fs.existsSync(this.storagePath)) {
      fs.mkdirSync(this.storagePath, { recursive: true });
    }
  }

  /**
   * Handle user messages from Discord
   */
  async handleUserMessage(message: string): Promise<void> {
    const parts = message.split(' ');
    const command = parts[0].toLowerCase();
    const content = parts.slice(1).join(' ');

    switch (command) {
      case '!log':
        await this.handleLog(content);
        break;

      case '!read':
        await this.handleRead();
        break;

      case '!context':
        await this.handleContext(parts.slice(1));
        break;

      case '!task':
        await this.handleTask(message.replace('!task', '').trim());
        break;

      default:
        // Ignore non-command messages
        break;
    }
  }

  /**
   * Handle !log command
   */
  private async handleLog(content: string): Promise<void> {
    if (!content) {
      await this.sendMessage('Usage: `!log <Entry>`');
      return;
    }

    const date = new Date().toISOString().split('T')[0];
    const logFile = path.join(this.storagePath, `${date}.md`);
    const timestamp = new Date().toLocaleTimeString();
    const entry = `\n[${timestamp}] ${content}`;

    await fs.promises.appendFile(logFile, entry);
    await this.sendMessage('✅ Logged.');
  }

  /**
   * Handle !read command
   */
  private async handleRead(): Promise<void> {
    const date = new Date().toISOString().split('T')[0];
    const logFile = path.join(this.storagePath, `${date}.md`);

    try {
      const logs = await fs.promises.readFile(logFile, 'utf-8');
      // Discord limit is 2000 chars
      const truncated = logs.slice(-1900);
      await this.sendMessage(`📄 **Daily Log:**\n${truncated}`);
    } catch {
      await this.sendMessage('📄 **Daily Log:**\n(Empty)');
    }
  }

  /**
   * Handle !context command
   */
  private async handleContext(args: string[]): Promise<void> {
    const subcommand = args[0]?.toLowerCase();

    if (subcommand === 'set') {
      const newContext = args.slice(1).join(' ');
      const contextFile = path.join(this.storagePath, 'CONTEXT.md');
      await fs.promises.writeFile(contextFile, newContext);
      await this.sendMessage('✅ Context updated.');
    } else {
      const contextFile = path.join(this.storagePath, 'CONTEXT.md');
      try {
        const ctx = await fs.promises.readFile(contextFile, 'utf-8');
        await this.sendMessage(`🧠 **Current Context:**\n${ctx}`);
      } catch {
        await this.sendMessage('🧠 **Current Context:**\nNo context defined.');
      }
    }
  }

  /**
   * Handle !task command
   */
  private async handleTask(title: string): Promise<void> {
    const taskTitle = title || 'Manual Task';

    this.taskRepo.create({
      brainId: this.id,
      title: taskTitle,
    });

    await this.sendMessage(`✅ Task "${taskTitle}" created.`);
  }
}
