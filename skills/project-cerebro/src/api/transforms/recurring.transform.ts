/**
 * Recurring task API transformation utilities
 * Bridges internal DB schema (pattern/active/cronExpression) 
 * with frontend API schema (scheduleType/enabled/scheduleConfig)
 */

import { RecurringTask } from '../../domain/types/schedule';

export interface ApiRecurringTask {
  id: string;
  brainId: string;
  title: string;
  description?: string;
  modelOverride?: string;
  scheduleType: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
  intervalMs?: number;
  scheduleConfig?: {
    hour?: number;
    minute?: number;
    day?: number;
  };
  nextRunAt: number;
  lastRunAt?: number;
  enabled: boolean;
  sendDiscordNotification?: boolean;
  triggersReport?: boolean;
  reportDelayMinutes?: number;
  createdAt: number;
  updatedAt: number;
}

/**
 * Parse cron expression to extract hour, minute, day
 */
function parseCronExpression(cronExpression?: string): { hour?: number; minute?: number; day?: number } {
  if (!cronExpression) return {};
  
  const parts = cronExpression.split(' ');
  if (parts.length !== 5) return {};
  
  const minute = parseInt(parts[0], 10);
  const hour = parseInt(parts[1], 10);
  const day = parseInt(parts[4], 10);
  
  return {
    minute: isNaN(minute) ? undefined : minute,
    hour: isNaN(hour) ? undefined : hour,
    day: isNaN(day) ? undefined : day,
  };
}

/**
 * Transform internal RecurringTask to API format
 */
export function toApiRecurringTask(task: RecurringTask): ApiRecurringTask {
  // Map pattern to scheduleType
  let scheduleType: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
  
  if (task.pattern === 'CUSTOM' && task.payload?.intervalMinutes) {
    scheduleType = 'INTERVAL';
  } else if (task.pattern === 'CUSTOM') {
    // Check cron expression to determine if it's hourly
    const cron = parseCronExpression(task.cronExpression);
    if (cron.hour === undefined && cron.minute !== undefined) {
      scheduleType = 'HOURLY';
    } else {
      scheduleType = 'DAILY'; // Default
    }
  } else {
    scheduleType = task.pattern as 'DAILY' | 'WEEKLY' | 'HOURLY' | 'INTERVAL';
  }
  
  // Parse schedule config from cron expression
  const scheduleConfig = parseCronExpression(task.cronExpression);
  
  // Calculate intervalMs from payload
  const intervalMs = task.payload?.intervalMinutes 
    ? task.payload.intervalMinutes * 60000 
    : undefined;
  
  return {
    id: task.id,
    brainId: task.brainId,
    title: task.title,
    description: task.description,
    modelOverride: task.modelOverride,
    scheduleType,
    intervalMs,
    scheduleConfig: Object.keys(scheduleConfig).length > 0 ? scheduleConfig : undefined,
    nextRunAt: task.nextExecutionAt || Date.now(),
    lastRunAt: task.lastExecutedAt,
    enabled: task.active,
    sendDiscordNotification: task.sendDiscordNotification,
    triggersReport: task.triggersReport,
    reportDelayMinutes: task.reportDelayMinutes,
    createdAt: task.createdAt,
    updatedAt: task.updatedAt,
  };
}

/**
 * Transform API update data to internal format
 */
export function fromApiUpdate(data: Partial<ApiRecurringTask>): Partial<{
  brainId?: string;
  title?: string;
  description?: string;
  modelOverride?: string;
  pattern?: string;
  cronExpression?: string;
  payload?: Record<string, any>;
  active?: boolean;
  nextExecutionAt?: number;
  sendDiscordNotification?: boolean;
  triggersReport?: boolean;
  reportDelayMinutes?: number;
}> {
  const result: any = {};
  
  // Basic fields
  if (data.brainId !== undefined) {
    result.brainId = data.brainId;
  }
  if (data.title !== undefined) {
    result.title = data.title;
  }
  if (data.description !== undefined) {
    result.description = data.description;
  }
  if (data.modelOverride !== undefined) {
    // Treat explicit "default" (or empty) as no override.
    if (data.modelOverride === '' || data.modelOverride === 'default') {
      result.modelOverride = undefined;
    } else {
      result.modelOverride = data.modelOverride;
    }
  }
  
  if (data.enabled !== undefined) {
    result.active = data.enabled;
  }
  
  if (data.scheduleType) {
    // Map scheduleType back to pattern
    if (data.scheduleType === 'INTERVAL') {
      result.pattern = 'CUSTOM';
    } else if (data.scheduleType === 'HOURLY') {
      result.pattern = 'CUSTOM';
    } else {
      result.pattern = data.scheduleType;
    }
    
    // Rebuild cron expression from scheduleConfig
    if (data.scheduleConfig) {
      const { hour = 0, minute = 0, day } = data.scheduleConfig;
      
      if (data.scheduleType === 'HOURLY') {
        result.cronExpression = `${minute} * * * *`;
      } else if (data.scheduleType === 'DAILY') {
        result.cronExpression = `${minute} ${hour} * * *`;
      } else if (data.scheduleType === 'WEEKLY' && day !== undefined) {
        result.cronExpression = `${minute} ${hour} * * ${day}`;
      }
    }
    
    // Handle interval
    if (data.scheduleType === 'INTERVAL' && data.intervalMs) {
      result.payload = { intervalMinutes: Math.round(data.intervalMs / 60000) };
    }
  }
  
  if (data.nextRunAt !== undefined) {
    result.nextExecutionAt = data.nextRunAt;
  }
  if (data.sendDiscordNotification !== undefined) {
    result.sendDiscordNotification = data.sendDiscordNotification;
  }
  if (data.triggersReport !== undefined) {
    result.triggersReport = data.triggersReport;
  }
  if (data.reportDelayMinutes !== undefined) {
    result.reportDelayMinutes = data.reportDelayMinutes;
  }

  return result;
}

/**
 * Compute next execution time from API format
 */
export function computeNextExecutionFromApi(
  scheduleType: string,
  scheduleConfig?: { hour?: number; minute?: number; day?: number },
  intervalMs?: number
): number {
  const now = Date.now();
  const date = new Date();

  switch (scheduleType) {
    case 'HOURLY':
      date.setMinutes(scheduleConfig?.minute || 0, 0, 0);
      date.setHours(date.getHours() + 1);
      return date.getTime();

    case 'DAILY':
      date.setHours(scheduleConfig?.hour || 0, scheduleConfig?.minute || 0, 0, 0);
      if (date.getTime() <= now) {
        date.setDate(date.getDate() + 1);
      }
      return date.getTime();

    case 'WEEKLY':
      const targetDay = scheduleConfig?.day || 1;
      const currentDay = date.getDay();
      let daysUntil = targetDay - currentDay;
      if (daysUntil < 0 || (daysUntil === 0 && date.getTime() > now)) {
        daysUntil += 7;
      }
      date.setDate(date.getDate() + daysUntil);
      date.setHours(scheduleConfig?.hour || 0, scheduleConfig?.minute || 0, 0, 0);
      return date.getTime();

    case 'INTERVAL':
      return now + (intervalMs || 3600000);

    default:
      return now + 3600000;
  }
}
