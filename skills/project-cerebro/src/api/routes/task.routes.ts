/**
 * Task routes
 */

import { FastifyInstance } from 'fastify';
import { TaskRepository } from '../../data/repositories';
import { TaskStatus, CreateTaskInput } from '../../domain/types';
import { TaskExecutorService } from '../../services/task-executor.service';

export function registerTaskRoutes(
  server: FastifyInstance,
  taskRepo: TaskRepository,
  taskExecutor: TaskExecutorService
): void {
  /**
   * GET /api/tasks
   * Get all tasks
   */
  server.get('/api/tasks', async () => {
    const tasks = taskRepo.findAll();
    return { tasks };
  });

  /**
   * GET /api/tasks/:id
   * Get specific task
   */
  server.get<{
    Params: { id: string };
  }>('/api/tasks/:id', async (request, reply) => {
    const { id } = request.params;
    const task = taskRepo.getById(id);
    return task;
  });

  /**
   * POST /api/tasks
   * Create a new task
   */
  server.post<{
    Body: CreateTaskInput;
  }>('/api/tasks', async (request, reply) => {
    const input = request.body;
    const task = taskRepo.create(input);
    reply.code(201);
    return task;
  });

  /**
   * PATCH /api/tasks/:id
   * Update a task
   */
  server.patch<{
    Params: { id: string };
    Body: Partial<CreateTaskInput> & { status?: TaskStatus };
  }>('/api/tasks/:id', async (request, reply) => {
    const { id } = request.params;
    const updates = request.body;
    const task = taskRepo.update({ id, ...updates });
    return task;
  });

  /**
   * DELETE /api/tasks/:id
   * Delete a task
   */
  server.delete<{
    Params: { id: string };
  }>('/api/tasks/:id', async (request, reply) => {
    const { id } = request.params;
    taskRepo.delete(id);
    reply.code(204);
  });

  /**
   * DELETE /api/tasks
   * Clear all tasks
   */
  server.delete('/api/tasks', async (request, reply) => {
    const tasks = taskRepo.findAll();
    for (const task of tasks) {
      taskRepo.delete(task.id);
    }
    return { success: true, deletedCount: tasks.length };
  });

  /**
   * GET /api/brains/:brainId/tasks
   * Get tasks for a brain
   */
  server.get<{
    Params: { brainId: string };
  }>('/api/brains/:brainId/tasks', async (request, reply) => {
    const { brainId } = request.params;
    const tasks = taskRepo.findByBrainId(brainId);
    return { tasks };
  });

  /**
   * POST /api/tasks/:id/execute
   * Execute a task immediately
   */
  server.post<{
    Params: { id: string };
  }>('/api/tasks/:id/execute', async (request, reply) => {
    const { id } = request.params;
    const task = taskRepo.getById(id);
    
    if (!task) {
      reply.code(404);
      return { error: 'Task not found' };
    }

    // Allow retrying FAILED tasks by resetting them to READY first.
    if (task.status === TaskStatus.FAILED) {
      taskRepo.update({
        id,
        status: TaskStatus.READY,
        error: undefined,
      });
      task.status = TaskStatus.READY;
    }

    if (task.status !== TaskStatus.READY) {
      reply.code(400);
      return { error: `Task cannot be executed (status: ${task.status})` };
    }

    // Execute the task asynchronously
    taskExecutor.executeTask(id).catch((error) => {
      console.error('Task execution failed:', error);
    });

    return { success: true, message: 'Task execution started' };
  });
}
