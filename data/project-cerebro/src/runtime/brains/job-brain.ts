/**
 * Job brain - specialized for job application tracking
 */

import { BaseBrain } from '../base-brain';
import { JobRepository } from '../../data/repositories';
import { JobStatus } from '../../domain/types';

export class JobBrain extends BaseBrain {
  private jobRepo: JobRepository;

  constructor(
    config: any,
    taskRepo: any,
    discordAdapter: any,
    openClawAdapter: any,
    taskExecutor: any,
    jobRepo: JobRepository
  ) {
    super(config, taskRepo, discordAdapter, openClawAdapter, taskExecutor);
    this.jobRepo = jobRepo;
  }

  /**
   * Handle user messages from Discord
   */
  async handleUserMessage(message: string): Promise<void> {
    const parts = message.split(' ');
    const command = parts[0].toLowerCase();

    switch (command) {
      case '!job':
        await this.handleJobCommand(parts.slice(1));
        break;

      case '!jobs':
        await this.handleListJobs();
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
   * Handle !job command
   */
  private async handleJobCommand(args: string[]): Promise<void> {
    const subcommand = args[0]?.toLowerCase();

    if (subcommand === 'add') {
      // !job add <company> | <title> | <url>
      const rest = args.slice(1).join(' ');
      const parts = rest.split('|').map((s) => s.trim());

      if (parts.length < 2) {
        await this.sendMessage('Usage: `!job add <company> | <title> | [url]`');
        return;
      }

      const [company, title, url] = parts;

      this.jobRepo.create({
        company,
        title,
        url,
        status: JobStatus.DISCOVERED,
      });

      await this.sendMessage(
        `✅ Job added: **${title}** at **${company}**${url ? ` - ${url}` : ''}`
      );
    } else if (subcommand === 'update') {
      // !job update <id> <status>
      const jobId = args[1];
      const newStatus = args[2]?.toUpperCase() as JobStatus;

      if (!jobId || !newStatus) {
        await this.sendMessage('Usage: `!job update <id> <status>`');
        return;
      }

      try {
        this.jobRepo.update({ id: jobId, status: newStatus });
        await this.sendMessage(`✅ Job ${jobId} updated to ${newStatus}`);
      } catch (error) {
        await this.sendMessage(`❌ Failed to update job: ${error}`);
      }
    } else {
      await this.sendMessage(
        'Usage:\n`!job add <company> | <title> | [url]`\n`!job update <id> <status>`'
      );
    }
  }

  /**
   * Handle !jobs command
   */
  private async handleListJobs(): Promise<void> {
    const jobs = this.jobRepo.findAll().slice(0, 10); // Limit to 10

    if (jobs.length === 0) {
      await this.sendMessage('📋 **No jobs tracked yet.**');
      return;
    }

    const lines = ['📋 **Recent Jobs:**', ''];
    for (const job of jobs) {
      lines.push(
        `**${job.title}** at **${job.company}** - ${job.status}${job.url ? ` - ${job.url}` : ''}`
      );
    }

    await this.sendMessage(lines.join('\n'));
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
