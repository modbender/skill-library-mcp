/**
 * Seed the database with starter tasks/recurring tasks.
 *
 * Safe-by-default:
 * - Does nothing if tasks or recurring tasks already exist (unless --force)
 * - Uses committed templates in config/seeds/*.template.json
 */

import fs from 'fs';
import path from 'path';
import { getConfig } from '../lib/config';
import { DatabaseConnection } from '../data/database';
import { TaskRepository, RecurringTaskRepository } from '../data/repositories';
import { computeNextExecutionFromApi } from '../api/transforms/recurring.transform';
import { logger } from '../lib/logger';

type SeedTask = {
  brainId: string;
  title: string;
  description?: string;
  payload?: Record<string, any>;
  modelOverride?: string;
  sendDiscordNotification?: boolean;
};

type SeedRecurring = {
  brainId: string;
  title: string;
  description?: string;
  modelOverride?: string;
  scheduleType: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
  intervalMinutes?: number;
  scheduleConfig?: { hour?: number; minute?: number; day?: number };
  enabled?: boolean;
  sendDiscordNotification?: boolean;
  triggersReport?: boolean;
  reportDelayMinutes?: number;
};

function readJson<T>(p: string): T {
  return JSON.parse(fs.readFileSync(p, 'utf-8')) as T;
}

function getArg(name: string): boolean {
  return process.argv.includes(name);
}

async function main() {
  const force = getArg('--force');

  const cfg = getConfig();
  const db = new DatabaseConnection(cfg.dbPath);
  db.init();

  const taskRepo = new TaskRepository(db);
  const recurringRepo = new RecurringTaskRepository(db);

  const existingTasks = taskRepo.findAll();
  const existingRecurring = recurringRepo.findAll();

  if (!force && (existingTasks.length > 0 || existingRecurring.length > 0)) {
    logger.info('Seed skipped: DB already has data', {
      tasks: existingTasks.length,
      recurring: existingRecurring.length,
    });
    return;
  }

  const seedDir = path.join(process.cwd(), 'config', 'seeds');
  const tasksPath = path.join(seedDir, 'tasks.template.json');
  const recurringPath = path.join(seedDir, 'recurring_tasks.template.json');

  if (!fs.existsSync(tasksPath) || !fs.existsSync(recurringPath)) {
    throw new Error(
      `Seed templates not found. Expected:\n- ${tasksPath}\n- ${recurringPath}`
    );
  }

  const tasks = readJson<SeedTask[]>(tasksPath);
  const recurring = readJson<SeedRecurring[]>(recurringPath);

  if (force) {
    // Best-effort cleanup only of tasks/recurring.
    for (const t of taskRepo.findAll()) taskRepo.delete(t.id);
    for (const r of recurringRepo.findAll()) recurringRepo.delete(r.id);
  }

  // Seed one-time tasks
  for (const t of tasks) {
    taskRepo.create({
      brainId: t.brainId,
      title: t.title,
      description: t.description,
      payload: t.payload,
      modelOverride: t.modelOverride,
      sendDiscordNotification: t.sendDiscordNotification,
    });
  }

  // Seed recurring tasks
  for (const r of recurring) {
    const nextExecutionAt = computeNextExecutionFromApi(
      r.scheduleType,
      r.scheduleConfig,
      r.intervalMinutes ? r.intervalMinutes * 60000 : undefined
    );

    let pattern: any;
    let cronExpression: string | undefined;
    let payload: Record<string, any> = {};

    switch (r.scheduleType) {
      case 'HOURLY':
        pattern = 'CUSTOM';
        cronExpression = `${r.scheduleConfig?.minute || 0} * * * *`;
        break;
      case 'DAILY':
        pattern = 'DAILY';
        cronExpression = `${r.scheduleConfig?.minute || 0} ${r.scheduleConfig?.hour || 0} * * *`;
        break;
      case 'WEEKLY':
        pattern = 'WEEKLY';
        cronExpression = `${r.scheduleConfig?.minute || 0} ${r.scheduleConfig?.hour || 0} * * ${r.scheduleConfig?.day || 1}`;
        break;
      case 'INTERVAL':
        pattern = 'CUSTOM';
        payload = { intervalMinutes: r.intervalMinutes || 60 };
        break;
      default:
        pattern = 'DAILY';
    }

    recurringRepo.create({
      brainId: r.brainId,
      title: r.title,
      description: r.description,
      modelOverride: r.modelOverride,
      pattern,
      cronExpression,
      payload,
      nextExecutionAt,
      sendDiscordNotification: r.sendDiscordNotification ?? true,
      triggersReport: r.triggersReport ?? false,
      reportDelayMinutes: r.reportDelayMinutes ?? 0,
    });

    // Respect enabled/disabled state
    if (r.enabled === false) {
      const created = recurringRepo.findAll().find((x) => x.title === r.title && x.brainId === r.brainId);
      if (created) recurringRepo.update({ id: created.id, active: false } as any);
    }
  }

  logger.info('Seed complete', {
    tasksSeeded: tasks.length,
    recurringSeeded: recurring.length,
    dbPath: cfg.dbPath,
  });
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
