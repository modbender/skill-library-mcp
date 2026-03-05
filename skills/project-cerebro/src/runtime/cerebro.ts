/**
 * Cerebro runtime orchestrator - main system coordinator
 */

import { logger } from '../lib/logger';
import { getConfig } from '../lib/config';
import { getDatabase, closeDatabase } from '../data/database';
import {
  TaskRepository,
  RecurringTaskRepository,
  JobRepository,
  BrainConfigRepository,
  BrainsRepository,
  JobApplicationsRepository,
} from '../data/repositories';
import {
  BrainService,
  SchedulerService,
  TaskExecutorService,
  ReportService,
} from '../services';
import { DiscordAdapter, OpenClawAdapter } from '../integrations';
import { ApiServer } from '../api/server';
import { OpenClawTaskExecutor } from './task-executor-impl';

export class CerebroRuntime {
  // Core services
  private brainService: BrainService;
  private taskExecutorService: TaskExecutorService;
  private schedulerService: SchedulerService;
  private reportService: ReportService;
  // digestService removed; digest tasks handled by Nexus

  // Repositories
  private taskRepo: TaskRepository;
  private recurringRepo: RecurringTaskRepository;
  private jobRepo: JobRepository;
  private brainConfigRepo: BrainConfigRepository;
  private brainsRepo: BrainsRepository;
  private jobApplicationsRepo: JobApplicationsRepository;

  // Integrations
  private discordAdapter: DiscordAdapter;
  private openClawAdapter: OpenClawAdapter;

  // API server
  private apiServer: ApiServer;

  // State
  private isRunning: boolean = false;

  // Brain configs for executor
  private brainConfigs: Map<string, any> = new Map();

  constructor() {
    const config = getConfig();

    // Initialize database
    const db = getDatabase(config.dbPath);

    // Initialize repositories
    this.taskRepo = new TaskRepository(db);
    this.recurringRepo = new RecurringTaskRepository(db);
    this.jobRepo = new JobRepository(db);
    this.brainConfigRepo = new BrainConfigRepository(db);
    this.brainsRepo = new BrainsRepository(db);
    this.jobApplicationsRepo = new JobApplicationsRepository(db);

    // Seed brains from JSON config (migration - only runs if DB is empty)
    this.brainsRepo.seedFromJson(config.brains);

    // Initialize services
    this.brainService = new BrainService();
    this.schedulerService = new SchedulerService(this.recurringRepo);
    this.reportService = new ReportService();

    // Initialize integrations
    this.openClawAdapter = new OpenClawAdapter(
      config.openClawGatewayUrl,
      config.openClawToken
    );
    // NOTE: DiscordAdapter is now just a thin wrapper that routes via OpenClaw.
    // We keep it for backwards compatibility, but routing destinations are now
    // channel-agnostic via config.brainTargets.
    this.discordAdapter = new DiscordAdapter('DISABLED', this.openClawAdapter);

    const getTarget = (brainId: string) => config.brainTargets.brains[brainId];

    // Store brain configs for task executor
    config.brains.brains.forEach((brain) => {
      const t = getTarget(brain.id);
      if (t) {
        this.brainConfigs.set(brain.id, {
          openClawAgentId: brain.openClawAgentId,
          notifyChannel: t.channel,
          notifyTarget: t.target,
          description: brain.description,
        });
      }
    });

    // Add nexus brain config (stored outside the brains[] list)
    {
      const t = getTarget(config.brains.nexus.id);
      if (t) {
        this.brainConfigs.set(config.brains.nexus.id, {
          openClawAgentId: config.brains.nexus.openClawAgentId,
          notifyChannel: t.channel,
          notifyTarget: t.target,
          description: config.brains.nexus.description,
        });
      }
    }

    // Digest brain removed; use Nexus for digest tasks.

    // Initialize task executor with OpenClaw implementation
    const taskExecutor = new OpenClawTaskExecutor(
      this.openClawAdapter,
      this.discordAdapter,
      this.brainConfigRepo,
      this.brainConfigs,
      this.reportService,
      this.taskRepo,
      this.recurringRepo
    );

    this.taskExecutorService = new TaskExecutorService(this.taskRepo, taskExecutor);

    // Initialize API server
    this.apiServer = new ApiServer(config.port, {
      brainService: this.brainService,
      taskRepo: this.taskRepo,
      recurringRepo: this.recurringRepo,
      reportService: this.reportService,
      taskExecutor: this.taskExecutorService,
      brainConfigRepo: this.brainConfigRepo,
      brainsRepo: this.brainsRepo,
      jobApplicationsRepo: this.jobApplicationsRepo,
    });

    logger.info('Cerebro runtime initialized');
  }

  /**
   * Start the runtime
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('Runtime already running');
      return;
    }

    logger.info('Starting Cerebro runtime');

    // Connect to Discord - Disabled, OpenClaw handles this
    // await this.discordAdapter.connect();

    // Initialize brains
    await this.brainService.initAll();

    // Start API server
    await this.apiServer.start();

    this.isRunning = true;
    logger.info('Cerebro runtime started');
  }

  /**
   * Stop the runtime
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      logger.warn('Runtime not running');
      return;
    }

    logger.info('Stopping Cerebro runtime');

    // Stop API server
    await this.apiServer.stop();

    // Disconnect from Discord - Disabled, OpenClaw handles this
    // await this.discordAdapter.disconnect();

    // Close database
    closeDatabase();

    this.isRunning = false;
    logger.info('Cerebro runtime stopped');
  }

  /**
   * Get services (for external access)
   */
  getServices() {
    return {
      brainService: this.brainService,
      taskExecutorService: this.taskExecutorService,
      schedulerService: this.schedulerService,
      reportService: this.reportService,
    };
  }

  /**
   * Get repositories (for external access)
   */
  getRepositories() {
    return {
      taskRepo: this.taskRepo,
      recurringRepo: this.recurringRepo,
      jobRepo: this.jobRepo,
      brainConfigRepo: this.brainConfigRepo,
      brainsRepo: this.brainsRepo,
      jobApplicationsRepo: this.jobApplicationsRepo,
    };
  }

  /**
   * Get integrations (for external access)
   */
  getIntegrations() {
    return {
      discordAdapter: this.discordAdapter,
      openClawAdapter: this.openClawAdapter,
    };
  }
}
