/**
 * Main entry point for Cerebro - refactored architecture
 */

import { logger, LogLevel } from './lib/logger';
import { getConfig } from './lib/config';
import { CerebroRuntime } from './runtime/cerebro';
import { HeartbeatLoop } from './runtime/heartbeat';
import { ContextBrain, JobBrain } from './runtime/brains';
import { BrainType } from './domain/types';
import * as fs from 'fs';
import * as path from 'path';

async function main() {
  try {
    // Load configuration
    const config = getConfig();

    // Set log level from config
    logger.setLevel(config.logLevel as LogLevel);

    logger.info('Starting Cerebro', {
      version: '2.0.0',
      environment: process.env.NODE_ENV || 'development',
    });

    // Load job profile for JobBrain
    let jobProfileData: any = null;
    const jobProfilePath = path.join(process.cwd(), 'data', 'job_profile.json');
    try {
      if (fs.existsSync(jobProfilePath)) {
        const raw = fs.readFileSync(jobProfilePath, 'utf-8');
        jobProfileData = JSON.parse(raw);
        logger.info('Loaded job profile for JobBrain', { path: jobProfilePath });
      } else {
        logger.warn('Job profile not found, JobBrain will work without profile data', { path: jobProfilePath });
      }
    } catch (err) {
      logger.error('Failed to load job profile', err as Error);
    }

    // Create runtime
    const runtime = new CerebroRuntime();
    const { brainService, taskExecutorService, schedulerService } = runtime.getServices();
    const { taskRepo, recurringRepo, jobRepo } = runtime.getRepositories();
    const { discordAdapter, openClawAdapter } = runtime.getIntegrations();

    // Register brains from configuration
    config.brains.brains.forEach((brainConfig) => {
      const target = config.brainTargets.brains[brainConfig.id];
      if (!target) {
        logger.warn('Target not found for brain', {
          brainId: brainConfig.id,
        });
        return;
      }

      const fullConfig = {
        id: brainConfig.id,
        name: brainConfig.name,
        type: brainConfig.type === 'job' ? BrainType.JOB : BrainType.CONTEXT,
        description: brainConfig.description,
        discordChannelId: target.target,
        openClawAgentId: brainConfig.openClawAgentId,
      };

      let brain;
      if (brainConfig.type === 'job') {
        // Add job profile to agentConfig for JobBrain
        const jobBrainConfig = {
          ...fullConfig,
          agentConfig: jobProfileData ? { jobProfile: jobProfileData } : undefined,
        };
        brain = new JobBrain(
          jobBrainConfig,
          taskRepo,
          discordAdapter,
          openClawAdapter,
          taskExecutorService,
          jobRepo
        );
      } else {
        brain = new ContextBrain(
          fullConfig,
          taskRepo,
          discordAdapter,
          openClawAdapter,
          taskExecutorService
        );
      }

      brainService.register(brain);
    });

    // Register nexus brain (general purpose brain)
    const nexusTarget = config.brainTargets.brains[config.brains.nexus.id];
    if (nexusTarget) {
      const nexusBrain = new ContextBrain(
        {
          id: 'nexus',
          name: 'Nexus',
          type: BrainType.CONTEXT,
          description: 'Main system interface and command routing',
          discordChannelId: nexusTarget.target,
          openClawAgentId: config.brains.nexus.openClawAgentId || 'nexus',
        },
        taskRepo,
        discordAdapter,
        openClawAdapter,
        taskExecutorService
      );
      brainService.register(nexusBrain);
    }

    // Digest brain removed; use Nexus for digest tasks.

    // Start runtime
    await runtime.start();

    // Start heartbeat loop (every 60 seconds)
    const heartbeat = new HeartbeatLoop(
      brainService,
      schedulerService,
      taskRepo,
      recurringRepo,
      60000
    );
    heartbeat.start();

    logger.info('Cerebro started successfully', {
      brainsRegistered: brainService.getAll().length,
      jobProfileLoaded: !!jobProfileData,
    });

    // Graceful shutdown
    const shutdown = async () => {
      logger.info('Shutting down Cerebro');
      heartbeat.stop();
      await runtime.stop();
      process.exit(0);
    };

    process.on('SIGINT', shutdown);
    process.on('SIGTERM', shutdown);
  } catch (error) {
    logger.error('Failed to start Cerebro', error as Error);
    process.exit(1);
  }
}

main();
