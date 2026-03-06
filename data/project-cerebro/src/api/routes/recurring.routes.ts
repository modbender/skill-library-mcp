/**
 * Recurring task routes
 */

import { FastifyInstance } from 'fastify';
import { RecurringTaskRepository, TaskRepository } from '../../data/repositories';
import { CreateRecurringTaskInput } from '../../domain/types';
import { TaskExecutorService } from '../../services/task-executor.service';
import { 
  toApiRecurringTask, 
  fromApiUpdate, 
  computeNextExecutionFromApi,
  ApiRecurringTask 
} from '../transforms/recurring.transform';

export function registerRecurringRoutes(
  server: FastifyInstance,
  recurringRepo: RecurringTaskRepository,
  taskRepo: TaskRepository,
  taskExecutor: TaskExecutorService
): void {
  /**
   * GET /api/recurring
   * Get all recurring tasks
   */
  server.get('/api/recurring', async () => {
    const tasks = recurringRepo.findAll();
    return { recurringTasks: tasks.map(toApiRecurringTask) };
  });

  /**
   * GET /api/recurring/:id
   * Get specific recurring task
   */
  server.get<{
    Params: { id: string };
  }>('/api/recurring/:id', async (request, reply) => {
    const { id } = request.params;
    const task = recurringRepo.getById(id);
    return toApiRecurringTask(task);
  });

  /**
   * POST /api/recurring
   * Create a new recurring task
   */
  server.post<{
    Body: {
      brainId: string;
      title: string;
      description?: string;
      modelOverride?: string;
      scheduleType: 'INTERVAL' | 'HOURLY' | 'DAILY' | 'WEEKLY';
      intervalMinutes?: number;
      scheduleConfig?: { hour?: number; minute?: number; day?: number };
    };
  }>('/api/recurring', async (request, reply) => {
    const body = request.body;
    
    // Validate required fields
    if (!body.brainId || !body.title || !body.scheduleType) {
      reply.code(400);
      return { error: 'Missing required fields: brainId, title, scheduleType' };
    }

    try {
      // Compute next execution time
      const nextExecutionAt = computeNextExecutionFromApi(
        body.scheduleType,
        body.scheduleConfig,
        body.intervalMinutes ? body.intervalMinutes * 60000 : undefined
      );

      // Map scheduleType to pattern and cronExpression
      let pattern: string;
      let cronExpression: string | undefined;
      let payload: Record<string, any> = {};

      switch (body.scheduleType) {
        case 'HOURLY':
          pattern = 'CUSTOM';
          cronExpression = `${body.scheduleConfig?.minute || 0} * * * *`;
          break;
        case 'DAILY':
          pattern = 'DAILY';
          cronExpression = `${body.scheduleConfig?.minute || 0} ${body.scheduleConfig?.hour || 0} * * *`;
          break;
        case 'WEEKLY':
          pattern = 'WEEKLY';
          cronExpression = `${body.scheduleConfig?.minute || 0} ${body.scheduleConfig?.hour || 0} * * ${body.scheduleConfig?.day || 1}`;
          break;
        case 'INTERVAL':
          pattern = 'CUSTOM';
          payload = { intervalMinutes: body.intervalMinutes || 60 };
          break;
        default:
          pattern = 'DAILY';
      }

      // Build payload for repository
      const input: CreateRecurringTaskInput = {
        brainId: body.brainId,
        title: body.title,
        description: body.description,
        pattern: pattern as any,
        cronExpression,
        payload,
        modelOverride: body.modelOverride,
        nextExecutionAt,
      };

      const task = recurringRepo.create(input);
      reply.code(201);
      return toApiRecurringTask(task);
    } catch (error) {
      console.error('Failed to create recurring task:', error);
      reply.code(500);
      return { error: 'Failed to create recurring task' };
    }
  });

  /**
   * PATCH /api/recurring/:id
   * Update a recurring task
   */
  server.patch<{
    Params: { id: string };
    Body: Partial<ApiRecurringTask>;
  }>('/api/recurring/:id', async (request, reply) => {
    const { id } = request.params;
    const updates = request.body;
    
    try {
      // Transform API updates to internal format
      const internalUpdates = fromApiUpdate(updates);
      
      // Recompute next execution if schedule changed
      if (updates.scheduleType && updates.scheduleConfig) {
        internalUpdates.nextExecutionAt = computeNextExecutionFromApi(
          updates.scheduleType,
          updates.scheduleConfig,
          updates.intervalMs
        );
      }
      
      const task = recurringRepo.update({ id, ...internalUpdates } as any);
      return toApiRecurringTask(task);
    } catch (error) {
      console.error('Failed to update recurring task:', error);
      reply.code(500);
      return { error: 'Failed to update recurring task' };
    }
  });

  /**
   * DELETE /api/recurring/:id
   * Delete a recurring task
   */
  server.delete<{
    Params: { id: string };
  }>('/api/recurring/:id', async (request, reply) => {
    const { id } = request.params;
    
    try {
      recurringRepo.delete(id);
      reply.code(204);
    } catch (error) {
      console.error('Failed to delete recurring task:', error);
      reply.code(500);
      return { error: 'Failed to delete recurring task' };
    }
  });

  /**
   * POST /api/recurring/:id/toggle
   * Toggle recurring task enabled/disabled
   */
  server.post<{
    Params: { id: string };
    Body: { enabled: boolean };
  }>('/api/recurring/:id/toggle', async (request, reply) => {
    const { id } = request.params;
    const { enabled } = request.body;
    
    try {
      const task = recurringRepo.getById(id);
      if (!task) {
        reply.code(404);
        return { error: 'Recurring task not found' };
      }

      recurringRepo.update({ id, active: enabled });
      // Re-fetch to get updated state
      const updated = recurringRepo.getById(id);
      return { success: true, task: toApiRecurringTask(updated) };
    } catch (error) {
      console.error('Failed to toggle recurring task:', error);
      reply.code(500);
      return { error: 'Failed to toggle recurring task' };
    }
  });

  /**
   * POST /api/recurring/:id/run
   * Run recurring task immediately (creates a task instance)
   */
  server.post<{
    Params: { id: string };
  }>('/api/recurring/:id/run', async (request, reply) => {
    const { id } = request.params;
    
    try {
      const recurringTask = recurringRepo.getById(id);
      
      if (!recurringTask) {
        reply.code(404);
        return { error: 'Recurring task not found' };
      }

      // Create a task instance
      const task = taskRepo.create({
        brainId: recurringTask.brainId,
        title: recurringTask.title,
        description: recurringTask.description,
        payload: {
          ...recurringTask.payload,
          recurringTaskId: recurringTask.id,
        },
        modelOverride: recurringTask.modelOverride,
        sendDiscordNotification: recurringTask.sendDiscordNotification,
      });

      // Execute immediately (async)
      taskExecutor.executeTask(task.id).catch((error) => {
        console.error('Recurring task execution failed:', error);
      });

      return { success: true, taskId: task.id };
    } catch (error) {
      console.error('Failed to run recurring task:', error);
      reply.code(500);
      return { error: 'Failed to run recurring task' };
    }
  });

  /**
   * GET /api/brains/:brainId/recurring
   * Get recurring tasks for a brain
   */
  server.get<{
    Params: { brainId: string };
  }>('/api/brains/:brainId/recurring', async (request, reply) => {
    const { brainId } = request.params;
    const tasks = recurringRepo.findByBrainId(brainId);
    return { recurringTasks: tasks.map(toApiRecurringTask) };
  });
}
